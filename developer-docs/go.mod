module github.com/pulumi/pulumi/developer-docs

go 1.23.0

replace github.com/pulumi/pulumi/sdk/v3 => ../sdk

require (
	github.com/pulumi/pulumi/sdk/v3 v3.156.0
	github.com/santhosh-tekuri/jsonschema/v5 v5.0.0
)
