// Copyright 2016-2021, Pulumi Corporation.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package resource

import (
	"fmt"
	"reflect"
	"sort"
	"strings"

	"github.com/pulumi/pulumi/sdk/v3/go/common/resource/archive"
	"github.com/pulumi/pulumi/sdk/v3/go/common/resource/asset"
	"github.com/pulumi/pulumi/sdk/v3/go/common/resource/sig"
	"github.com/pulumi/pulumi/sdk/v3/go/common/slice"
	"github.com/pulumi/pulumi/sdk/v3/go/common/tokens"
	"github.com/pulumi/pulumi/sdk/v3/go/common/util/contract"
	"github.com/pulumi/pulumi/sdk/v3/go/common/util/mapper"
)

// PropertyKey is the name of a property.
type PropertyKey tokens.Name

// PropertyMap is a simple map keyed by property name with "JSON-like" values.
type PropertyMap map[PropertyKey]PropertyValue

// NewPropertyMap turns a struct into a property map, using any JSON tags inside to determine naming.
func NewPropertyMap(s interface{}) PropertyMap {
	return NewPropertyMapRepl(s, nil, nil)
}

// NewPropertyMapRepl turns a struct into a property map, using any JSON tags inside to determine naming.  If non-nil
// replk or replv function(s) are provided, key and/or value transformations are performed during the mapping.
func NewPropertyMapRepl(s interface{},
	replk func(string) (PropertyKey, bool), replv func(interface{}) (PropertyValue, bool),
) PropertyMap {
	m, err := mapper.Unmap(s)
	contract.Assertf(err == nil, "Struct of properties failed to map correctly: %v", err)
	return NewPropertyMapFromMapRepl(m, replk, replv)
}

// NewPropertyMapFromMap creates a resource map from a regular weakly typed JSON-like map.
func NewPropertyMapFromMap(m map[string]interface{}) PropertyMap {
	return NewPropertyMapFromMapRepl(m, nil, nil)
}

// NewPropertyMapFromMapRepl optionally replaces keys/values in an existing map while creating a new resource map.
func NewPropertyMapFromMapRepl(m map[string]interface{},
	replk func(string) (PropertyKey, bool), replv func(interface{}) (PropertyValue, bool),
) PropertyMap {
	result := make(PropertyMap)
	for k, v := range m {
		key := PropertyKey(k)
		if replk != nil {
			if rk, repl := replk(k); repl {
				key = rk
			}
		}
		result[key] = NewPropertyValueRepl(v, replk, replv)
	}
	return result
}

// PropertyValue is the value of a property, limited to a select few types (see below).
type PropertyValue struct {
	V interface{}
}

// Computed represents the absence of a property value, because it will be computed at some point in the future.  It
// contains a property value which represents the underlying expected type of the eventual property value.
type Computed struct {
	Element PropertyValue // the eventual value (type) of the computed property.
}

// Output is a property value that will eventually be computed by the resource provider.  If an output property is
// encountered, it means the resource has not yet been created, and so the output value is unavailable.  Note that an
// output property is a special case of computed, but carries additional semantic meaning.
type Output struct {
	Element      PropertyValue // the value of this output if it is resolved.
	Known        bool          `json:"-"` // true if this output's value is known.
	Secret       bool          `json:"-"` // true if this output's value is secret.
	Dependencies []URN         `json:"-"` // the dependencies associated with this output.
}

// Secret indicates that the underlying value should be persisted securely.
//
// In order to facilitate the ability to distinguish secrets with identical plaintext in downstream code that may
// want to cache a secret's ciphertext, secret PropertyValues hold the address of the Secret. If a secret must be
// copied, its value--not its address--should be copied.
type Secret struct {
	Element PropertyValue
}

// ResourceReference is a property value that represents a reference to a Resource. The reference captures the
// resource's URN, ID, and the version of its containing package. Note that there are several cases to consider with
// respect to the ID:
//
//   - The reference may not contain an ID if the referenced resource is a component resource. In this case, the ID will
//     be null.
//   - The ID may be unknown (in which case it will be the unknown property value)
//   - Otherwise, the ID must be a string.
//
//nolint:revive
type ResourceReference struct {
	URN            URN
	ID             PropertyValue
	PackageVersion string
}

func (ref ResourceReference) IDString() (value string, hasID bool) {
	switch {
	case ref.ID.IsComputed():
		return "", true
	case ref.ID.IsString():
		return ref.ID.StringValue(), true
	default:
		return "", false
	}
}

func (ref ResourceReference) Equal(other ResourceReference) bool {
	if ref.URN != other.URN {
		return false
	}

	vid, oid := ref.ID, other.ID
	if vid.IsComputed() && oid.IsComputed() {
		return true
	}
	return vid.DeepEquals(oid)
}

type ReqError struct {
	K PropertyKey
}

func IsReqError(err error) bool {
	_, isreq := err.(*ReqError)
	return isreq
}

func (err *ReqError) Error() string {
	return fmt.Sprintf("required property '%v' is missing", err.K)
}

// HasValue returns true if the slot associated with the given property key contains a real value.  It returns false
// if a value is null or an output property that is awaiting a value to be assigned.  That is to say, HasValue indicates
// a semantically meaningful value is present (even if it's a computed one whose concrete value isn't yet evaluated).
func (props PropertyMap) HasValue(k PropertyKey) bool {
	v, has := props[k]
	return has && v.HasValue()
}

// ContainsUnknowns returns true if the property map contains at least one unknown value.
func (props PropertyMap) ContainsUnknowns() bool {
	for _, v := range props {
		if v.ContainsUnknowns() {
			return true
		}
	}
	return false
}

// ContainsSecrets returns true if the property map contains at least one secret value.
func (props PropertyMap) ContainsSecrets() bool {
	for _, v := range props {
		if v.ContainsSecrets() {
			return true
		}
	}
	return false
}

// Mappable returns a mapper-compatible object map, suitable for deserialization into structures.
func (props PropertyMap) Mappable() map[string]interface{} {
	return props.MapRepl(nil, nil)
}

// MapRepl returns a mapper-compatible object map, suitable for deserialization into structures.  A key and/or value
// replace function, replk/replv, may be passed that will replace elements using custom logic if appropriate.
func (props PropertyMap) MapRepl(replk func(string) (string, bool),
	replv func(PropertyValue) (interface{}, bool),
) map[string]interface{} {
	obj := make(map[string]interface{})
	for _, k := range props.StableKeys() {
		key := string(k)
		if replk != nil {
			if rk, repk := replk(key); repk {
				key = rk
			}
		}
		obj[key] = props[k].MapRepl(replk, replv)
	}
	return obj
}

// Copy makes a shallow copy of the map.
func (props PropertyMap) Copy() PropertyMap {
	new := make(PropertyMap)
	for k, v := range props {
		new[k] = v
	}
	return new
}

// StableKeys returns all of the map's keys in a stable order.
func (props PropertyMap) StableKeys() []PropertyKey {
	sorted := slice.Prealloc[PropertyKey](len(props))
	for k := range props {
		sorted = append(sorted, k)
	}
	sort.Slice(sorted, func(i, j int) bool { return sorted[i] < sorted[j] })
	return sorted
}

// PropertyValueType enumerates the actual types that may be stored in a PropertyValue.
//
//nolint:lll
type PropertyValueType interface {
	bool | float64 | string | *asset.Asset | *archive.Archive | Computed | Output | *Secret | ResourceReference | []PropertyValue | PropertyMap
}

// NewProperty creates a new PropertyValue.
func NewProperty[T PropertyValueType](v T) PropertyValue {
	return PropertyValue{v}
}

func NewNullProperty() PropertyValue                                 { return PropertyValue{nil} }
func NewBoolProperty(v bool) PropertyValue                           { return PropertyValue{v} }
func NewNumberProperty(v float64) PropertyValue                      { return PropertyValue{v} }
func NewStringProperty(v string) PropertyValue                       { return PropertyValue{v} }
func NewArrayProperty(v []PropertyValue) PropertyValue               { return PropertyValue{v} }
func NewAssetProperty(v *asset.Asset) PropertyValue                  { return PropertyValue{v} }
func NewArchiveProperty(v *archive.Archive) PropertyValue            { return PropertyValue{v} }
func NewObjectProperty(v PropertyMap) PropertyValue                  { return PropertyValue{v} }
func NewComputedProperty(v Computed) PropertyValue                   { return PropertyValue{v} }
func NewOutputProperty(v Output) PropertyValue                       { return PropertyValue{v} }
func NewSecretProperty(v *Secret) PropertyValue                      { return PropertyValue{v} }
func NewResourceReferenceProperty(v ResourceReference) PropertyValue { return PropertyValue{v} }

func MakeComputed(v PropertyValue) PropertyValue {
	return NewProperty(Computed{Element: v})
}

func MakeOutput(v PropertyValue) PropertyValue {
	return NewProperty(Output{Element: v})
}

func MakeSecret(v PropertyValue) PropertyValue {
	return NewProperty(&Secret{Element: v})
}

// MakeComponentResourceReference creates a reference to a component resource.
func MakeComponentResourceReference(urn URN, packageVersion string) PropertyValue {
	return NewProperty(ResourceReference{
		URN:            urn,
		PackageVersion: packageVersion,
	})
}

// MakeCustomResourceReference creates a reference to a custom resource. If the resource's ID is the empty string, it
// will be treated as unknown.
func MakeCustomResourceReference(urn URN, id ID, packageVersion string) PropertyValue {
	idProp := NewProperty(string(id))
	if id == "" {
		idProp = MakeComputed(NewProperty(""))
	}

	return NewProperty(ResourceReference{
		ID:             idProp,
		URN:            urn,
		PackageVersion: packageVersion,
	})
}

// NewPropertyValue turns a value into a property value, provided it is of a legal "JSON-like" kind.
func NewPropertyValue(v interface{}) PropertyValue {
	return NewPropertyValueRepl(v, nil, nil)
}

// NewPropertyValueRepl turns a value into a property value, provided it is of a legal "JSON-like" kind.  The
// replacement functions, replk and replv, may be supplied to transform keys and/or values as the mapping takes place.
func NewPropertyValueRepl(v interface{},
	replk func(string) (PropertyKey, bool), replv func(interface{}) (PropertyValue, bool),
) PropertyValue {
	// If a replacement routine is supplied, use that.
	if replv != nil {
		if rv, repl := replv(v); repl {
			return rv
		}
	}

	// If nil, easy peasy, just return a null.
	if v == nil {
		return NewNullProperty()
	}

	// Else, check for some known primitive types.
	switch t := v.(type) {
	case bool:
		return NewProperty(t)
	case int:
		return NewProperty(float64(t))
	case uint:
		return NewProperty(float64(t))
	case int32:
		return NewProperty(float64(t))
	case uint32:
		return NewProperty(float64(t))
	case int64:
		return NewProperty(float64(t))
	case uint64:
		return NewProperty(float64(t))
	case float32:
		return NewProperty(float64(t))
	case float64:
		return NewProperty(t)
	case string:
		return NewProperty(t)
	case *asset.Asset:
		return NewProperty(t)
	case *archive.Archive:
		return NewProperty(t)
	case Computed:
		return NewProperty(t)
	case Output:
		return NewProperty(t)
	case *Secret:
		return NewProperty(t)
	case ResourceReference:
		return NewProperty(t)
	case PropertyValue:
		return t
	}

	// Next, see if it's an array, slice, pointer or struct, and handle each accordingly.
	rv := reflect.ValueOf(v)
	//nolint:exhaustive // We intentionally only handle some types here.
	switch rk := rv.Type().Kind(); rk {
	case reflect.Array, reflect.Slice:
		// If an array or slice, just create an array out of it.
		arr := []PropertyValue{}
		for i := 0; i < rv.Len(); i++ {
			elem := rv.Index(i)
			arr = append(arr, NewPropertyValueRepl(elem.Interface(), replk, replv))
		}
		return NewProperty(arr)
	case reflect.Ptr:
		// If a pointer, recurse and return the underlying value.
		if rv.IsNil() {
			return NewNullProperty()
		}
		return NewPropertyValueRepl(rv.Elem().Interface(), replk, replv)
	case reflect.Map:
		// If a map, create a new property map, provided the keys and values are okay.
		obj := PropertyMap{}
		for iter := rv.MapRange(); iter.Next(); {
			key := iter.Key()
			if key.Kind() != reflect.String {
				contract.Failf("Unrecognized PropertyMap key type %v", key.Type())
			}

			pk := PropertyKey(key.String())
			if replk != nil {
				if rk, repl := replk(string(pk)); repl {
					pk = rk
				}
			}

			val := iter.Value().Interface()
			pv := NewPropertyValueRepl(val, replk, replv)
			obj[pk] = pv
		}
		return NewProperty(obj)
	case reflect.String:
		return NewProperty(rv.String())
	case reflect.Struct:
		obj := NewPropertyMapRepl(v, replk, replv)
		return NewProperty(obj)
	default:
		contract.Failf("Unrecognized value type: type=%v kind=%v", rv.Type(), rk)
		return NewNullProperty()
	}
}

// HasValue returns true if a value is semantically meaningful.
func (v PropertyValue) HasValue() bool {
	if v.IsOutput() {
		return v.OutputValue().Known
	}
	return !v.IsNull()
}

// ContainsUnknowns returns true if the property value contains at least one unknown (deeply).
func (v PropertyValue) ContainsUnknowns() bool {
	if v.IsComputed() || (v.IsOutput() && !v.OutputValue().Known) {
		return true
	} else if v.IsArray() {
		for _, e := range v.ArrayValue() {
			if e.ContainsUnknowns() {
				return true
			}
		}
	} else if v.IsObject() {
		return v.ObjectValue().ContainsUnknowns()
	} else if v.IsSecret() {
		return v.SecretValue().Element.ContainsUnknowns()
	}
	return false
}

// ContainsSecrets returns true if the property value contains at least one secret (deeply).
func (v PropertyValue) ContainsSecrets() bool {
	if v.IsSecret() {
		return true
	} else if v.IsComputed() {
		return v.Input().Element.ContainsSecrets()
	} else if v.IsOutput() {
		return v.OutputValue().Secret || v.OutputValue().Element.ContainsSecrets()
	} else if v.IsArray() {
		for _, e := range v.ArrayValue() {
			if e.ContainsSecrets() {
				return true
			}
		}
	} else if v.IsObject() {
		return v.ObjectValue().ContainsSecrets()
	}
	return false
}

// BoolValue fetches the underlying bool value (panicking if it isn't a bool).
func (v PropertyValue) BoolValue() bool { return v.V.(bool) }

// NumberValue fetches the underlying number value (panicking if it isn't a number).
func (v PropertyValue) NumberValue() float64 { return v.V.(float64) }

// StringValue fetches the underlying string value (panicking if it isn't a string).
func (v PropertyValue) StringValue() string { return v.V.(string) }

// ArrayValue fetches the underlying array value (panicking if it isn't a array).
func (v PropertyValue) ArrayValue() []PropertyValue { return v.V.([]PropertyValue) }

// AssetValue fetches the underlying asset value (panicking if it isn't an asset).
func (v PropertyValue) AssetValue() *asset.Asset { return v.V.(*asset.Asset) }

// ArchiveValue fetches the underlying archive value (panicking if it isn't an archive).
func (v PropertyValue) ArchiveValue() *archive.Archive { return v.V.(*archive.Archive) }

// ObjectValue fetches the underlying object value (panicking if it isn't a object).
func (v PropertyValue) ObjectValue() PropertyMap { return v.V.(PropertyMap) }

// Input fetches the underlying computed value (panicking if it isn't a computed).
func (v PropertyValue) Input() Computed { return v.V.(Computed) }

// OutputValue fetches the underlying output value (panicking if it isn't a output).
func (v PropertyValue) OutputValue() Output { return v.V.(Output) }

// SecretValue fetches the underlying secret value (panicking if it isn't a secret).
func (v PropertyValue) SecretValue() *Secret { return v.V.(*Secret) }

// ResourceReferenceValue fetches the underlying resource reference value (panicking if it isn't a resource reference).
func (v PropertyValue) ResourceReferenceValue() ResourceReference { return v.V.(ResourceReference) }

// IsNull returns true if the underlying value is a null.
func (v PropertyValue) IsNull() bool {
	return v.V == nil
}

// IsBool returns true if the underlying value is a bool.
func (v PropertyValue) IsBool() bool {
	_, is := v.V.(bool)
	return is
}

// IsNumber returns true if the underlying value is a number.
func (v PropertyValue) IsNumber() bool {
	_, is := v.V.(float64)
	return is
}

// IsString returns true if the underlying value is a string.
func (v PropertyValue) IsString() bool {
	_, is := v.V.(string)
	return is
}

// IsArray returns true if the underlying value is an array.
func (v PropertyValue) IsArray() bool {
	_, is := v.V.([]PropertyValue)
	return is
}

// IsAsset returns true if the underlying value is an asset.
func (v PropertyValue) IsAsset() bool {
	_, is := v.V.(*asset.Asset)
	return is
}

// IsArchive returns true if the underlying value is an archive.
func (v PropertyValue) IsArchive() bool {
	_, is := v.V.(*archive.Archive)
	return is
}

// IsObject returns true if the underlying value is an object.
func (v PropertyValue) IsObject() bool {
	_, is := v.V.(PropertyMap)
	return is
}

// IsComputed returns true if the underlying value is a computed value.
func (v PropertyValue) IsComputed() bool {
	_, is := v.V.(Computed)
	return is
}

// IsOutput returns true if the underlying value is an output value.
func (v PropertyValue) IsOutput() bool {
	_, is := v.V.(Output)
	return is
}

// IsSecret returns true if the underlying value is a secret value.
func (v PropertyValue) IsSecret() bool {
	_, is := v.V.(*Secret)
	return is
}

// IsResourceReference returns true if the underlying value is a resource reference value.
func (v PropertyValue) IsResourceReference() bool {
	_, is := v.V.(ResourceReference)
	return is
}

// TypeString returns a type representation of the property value's holder type.
func (v PropertyValue) TypeString() string {
	if v.IsNull() {
		return "null"
	} else if v.IsBool() {
		return "bool"
	} else if v.IsNumber() {
		return "number"
	} else if v.IsString() {
		return "string"
	} else if v.IsArray() {
		return "[]"
	} else if v.IsAsset() {
		return "asset"
	} else if v.IsArchive() {
		return "archive"
	} else if v.IsObject() {
		return "object"
	} else if v.IsComputed() {
		return "output<" + v.Input().Element.TypeString() + ">"
	} else if v.IsOutput() {
		if !v.OutputValue().Known {
			return MakeComputed(v.OutputValue().Element).TypeString()
		} else if v.OutputValue().Secret {
			return MakeSecret(v.OutputValue().Element).TypeString()
		}
		return v.OutputValue().Element.TypeString()
	} else if v.IsSecret() {
		return "secret<" + v.SecretValue().Element.TypeString() + ">"
	} else if v.IsResourceReference() {
		ref := v.ResourceReferenceValue()
		return fmt.Sprintf("resourceReference(%q, %q, %q)", ref.URN, ref.ID, ref.PackageVersion)
	}
	contract.Failf("Unrecognized PropertyValue type")
	return ""
}

// Mappable returns a mapper-compatible value, suitable for deserialization into structures.
func (v PropertyValue) Mappable() interface{} {
	return v.MapRepl(nil, nil)
}

// MapRepl returns a mapper-compatible object map, suitable for deserialization into structures.  A key and/or value
// replace function, replk/replv, may be passed that will replace elements using custom logic if appropriate.
func (v PropertyValue) MapRepl(replk func(string) (string, bool),
	replv func(PropertyValue) (interface{}, bool),
) interface{} {
	if replv != nil {
		if rv, repv := replv(v); repv {
			return rv
		}
	}
	if v.IsNull() {
		return nil
	} else if v.IsBool() {
		return v.BoolValue()
	} else if v.IsNumber() {
		return v.NumberValue()
	} else if v.IsString() {
		return v.StringValue()
	} else if v.IsArray() {
		arr := []interface{}{}
		for _, e := range v.ArrayValue() {
			arr = append(arr, e.MapRepl(replk, replv))
		}
		return arr
	} else if v.IsAsset() {
		return v.AssetValue()
	} else if v.IsArchive() {
		return v.ArchiveValue()
	} else if v.IsComputed() {
		return v.Input()
	} else if v.IsOutput() {
		return v.OutputValue()
	} else if v.IsSecret() {
		return v.SecretValue()
	} else if v.IsResourceReference() {
		return v.ResourceReferenceValue()
	}
	contract.Assertf(v.IsObject(), "v is not Object '%v' instead", v.TypeString())
	return v.ObjectValue().MapRepl(replk, replv)
}

// String implements the fmt.Stringer interface to add slightly more information to the output.
func (v PropertyValue) String() string {
	if v.IsComputed() {
		// For computed properties, show the type followed by an empty object string.
		return fmt.Sprintf("%v{}", v.TypeString())
	} else if v.IsOutput() {
		if !v.OutputValue().Known {
			return MakeComputed(v.OutputValue().Element).String()
		} else if v.OutputValue().Secret {
			return MakeSecret(v.OutputValue().Element).String()
		}
		return v.OutputValue().Element.String()
	}
	// For all others, just display the underlying property value.
	return fmt.Sprintf("{%v}", v.V)
}

// Property is a pair of key and value.
type Property struct {
	Key   PropertyKey
	Value PropertyValue
}

// SigKey is sometimes used to encode type identity inside of a map.  This is required when flattening into ordinary
// maps, like we do when performing serialization, to ensure recoverability of type identities later on.
const SigKey = sig.Key

// HasSig checks to see if the given property map contains the specific signature match.
func HasSig(obj PropertyMap, match string) bool {
	if sig, hassig := obj[SigKey]; hassig {
		return sig.IsString() && sig.StringValue() == match
	}
	return false
}

// SecretSig is the unique secret signature.
const SecretSig = sig.Secret

// ResourceReferenceSig is the unique resource reference signature.
const ResourceReferenceSig = sig.ResourceReference

// OutputValueSig is the unique output value signature.
const OutputValueSig = sig.OutputValue

// IsInternalPropertyKey returns true if the given property key is an internal key that should not be displayed to
// users.
func IsInternalPropertyKey(key PropertyKey) bool {
	return strings.HasPrefix(string(key), "__")
}
