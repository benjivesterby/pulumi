// Copyright 2016-2020, Pulumi Corporation.
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

package auto

import (
	"context"
	"io"

	"github.com/pulumi/pulumi/sdk/v3/go/auto/optlist"
	"github.com/pulumi/pulumi/sdk/v3/go/auto/optremove"
	"github.com/pulumi/pulumi/sdk/v3/go/common/apitype"
	"github.com/pulumi/pulumi/sdk/v3/go/common/workspace"

	"github.com/pulumi/pulumi/sdk/v3/go/pulumi"
)

// Workspace is the execution context containing a single Pulumi project, a program, and multiple stacks.
// Workspaces are used to manage the execution environment, providing various utilities such as plugin
// installation, environment configuration ($PULUMI_HOME), and creation, deletion, and listing of Stacks.
type Workspace interface {
	// ProjectSettings returns the settings object for the current project if any.
	ProjectSettings(context.Context) (*workspace.Project, error)
	// SaveProjectSettings overwrites the settings object in the current project.
	// There can only be a single project per workspace. Fails is new project name does not match old.
	SaveProjectSettings(context.Context, *workspace.Project) error
	// StackSettings returns the settings object for the stack matching the specified stack name if any.
	StackSettings(context.Context, string) (*workspace.ProjectStack, error)
	// SaveStackSettings overwrites the settings object for the stack matching the specified stack name.
	SaveStackSettings(context.Context, string, *workspace.ProjectStack) error
	// SerializeArgsForOp is hook to provide additional args to every CLI commands before they are executed.
	// Provided with stack name,
	// returns a list of args to append to an invoked command ["--config=...", ].
	SerializeArgsForOp(context.Context, string) ([]string, error)
	// PostCommandCallback is a hook executed after every command. Called with the stack name.
	// An extensibility point to perform workspace cleanup (CLI operations may create/modify a Pulumi.stack.yaml).
	PostCommandCallback(context.Context, string) error
	// AddEnvironments adds the specified environments to the provided stack's configuration.
	AddEnvironments(context.Context, string, ...string) error
	// ListEnvironments returns the list of environments from the provided stack's configuration.
	ListEnvironments(context.Context, string) ([]string, error)
	// RemoveEnvironment removes the specified environment from the provided stack's configuration.
	RemoveEnvironment(context.Context, string, string) error
	// GetConfig returns the value associated with the specified stack name and key,
	// scoped to the current workspace.
	GetConfig(context.Context, string, string) (ConfigValue, error)
	// GetConfigWithOptions returns the value associated with the specified stack name and key
	// using the optional ConfigOptions,
	// scoped to the current workspace.
	GetConfigWithOptions(context.Context, string, string, *ConfigOptions) (ConfigValue, error)
	// GetAllConfig returns the config map for the specified stack name, scoped to the current workspace.
	GetAllConfig(context.Context, string) (ConfigMap, error)
	// GetAllConfigWithOptions returns the config map for the specified stack name
	// using the optional GetAllConfigOptions,
	// scoped to the current workspace.
	GetAllConfigWithOptions(context.Context, string, *GetAllConfigOptions) (ConfigMap, error)
	// SetConfig sets the specified key-value pair on the provided stack name.
	SetConfig(context.Context, string, string, ConfigValue) error
	// SetConfigWithOptions sets the specified key-value pair on the provided stack name
	// using the optional ConfigOptions.
	SetConfigWithOptions(context.Context, string, string, ConfigValue, *ConfigOptions) error
	// SetAllConfig sets all values in the provided config map for the specified stack name.
	SetAllConfig(context.Context, string, ConfigMap) error
	// SetAllConfigWithOptions sets all values in the provided config map for the specified stack name
	// using the optional ConfigOptions.
	SetAllConfigWithOptions(context.Context, string, ConfigMap, *ConfigOptions) error
	// RemoveConfig removes the specified key-value pair on the provided stack name.
	RemoveConfig(context.Context, string, string) error
	// RemoveConfigWithOptions removes the specified key-value pair on the provided stack name
	// using the optional ConfigOptions.
	RemoveConfigWithOptions(context.Context, string, string, *ConfigOptions) error
	// RemoveAllConfig removes all values in the provided key list for the specified stack name.
	RemoveAllConfig(context.Context, string, []string) error
	// RemoveAllConfigWithOptions removes all values in the provided key list for the specified stack name
	// using the optional ConfigOptions.
	RemoveAllConfigWithOptions(context.Context, string, []string, *ConfigOptions) error
	// RefreshConfig gets and sets the config map used with the last Update for Stack matching stack name.
	RefreshConfig(context.Context, string) (ConfigMap, error)
	// GetTag returns the value associated with the specified stack name and key.
	GetTag(context.Context, string, string) (string, error)
	// SetTag sets the specified key-value pair on the provided stack name.
	SetTag(context.Context, string, string, string) error
	// RemoveTag removes the specified key-value pair on the provided stack name.
	RemoveTag(context.Context, string, string) error
	// ListTags returns the tag map for the specified stack name.
	ListTags(context.Context, string) (map[string]string, error)
	// GetEnvVars returns the environment values scoped to the current workspace.
	GetEnvVars() map[string]string
	// SetEnvVars sets the specified map of environment values scoped to the current workspace.
	// These values will be passed to all Workspace and Stack level commands.
	SetEnvVars(map[string]string) error
	// SetEnvVar sets the specified environment value scoped to the current workspace.
	// This value will be passed to all Workspace and Stack level commands.
	SetEnvVar(string, string)
	// UnsetEnvVar unsets the specified environment value scoped to the current workspace.
	// This value will be removed from all Workspace and Stack level commands.
	UnsetEnvVar(string)
	// WorkDir returns the working directory to run Pulumi CLI commands.
	WorkDir() string
	// PulumiCommand returns the PulumiCommand instance that is used to run PulumiCommand CLI commands.
	PulumiCommand() PulumiCommand
	// PulumiHome returns the directory override for CLI metadata if set.
	// This customizes the location of $PULUMI_HOME where metadata is stored and plugins are installed.
	PulumiHome() string
	// PulumiVersion returns the version of the underlying Pulumi CLI/Engine.
	PulumiVersion() string
	// WhoAmI returns the currently authenticated user.
	WhoAmI(context.Context) (string, error)
	// WhoAmIDetails returns detailed information about the currently
	// logged-in Pulumi identity.
	WhoAmIDetails(ctx context.Context) (WhoAmIResult, error)
	// ChangeStackSecretsProvider edits the secrets provider for the given stack.
	ChangeStackSecretsProvider(
		ctx context.Context, stackName, newSecretsProvider string, opts *ChangeSecretsProviderOptions,
	) error
	// Stack returns a summary of the currently selected stack, if any.
	Stack(context.Context) (*StackSummary, error)
	// CreateStack creates and sets a new stack with the stack name, failing if one already exists.
	CreateStack(context.Context, string) error
	// SelectStack selects and sets an existing stack matching the stack name, failing if none exists.
	SelectStack(context.Context, string) error
	// RemoveStack deletes the stack and all associated configuration and history.
	RemoveStack(context.Context, string, ...optremove.Option) error
	// ListStacks returns all Stacks from the underlying backend based on the provided options.
	// This queries the backend service and may return stacks not present in the Workspace.
	ListStacks(context.Context, ...optlist.Option) ([]StackSummary, error)
	// InstallPlugin acquires the plugin matching the specified name and version.
	InstallPlugin(context.Context, string, string) error
	// InstallPluginFromServer acquires the plugin matching the specified name and version.
	InstallPluginFromServer(context.Context, string, string, string) error
	// RemovePlugin deletes the plugin matching the specified name and version.
	RemovePlugin(context.Context, string, string) error
	// ListPlugins lists all installed plugins.
	ListPlugins(context.Context) ([]workspace.PluginInfo, error)
	// Program returns the program `pulumi.RunFunc` to be used for Preview/Update if any.
	// If none is specified, the stack will refer to ProjectSettings for this information.
	Program() pulumi.RunFunc
	// SetProgram sets the program associated with the Workspace to the specified `pulumi.RunFunc`.
	SetProgram(pulumi.RunFunc)
	// ExportStack exports the deployment state of the stack matching the given name.
	// This can be combined with ImportStack to edit a stack's state (such as recovery from failed deployments).
	ExportStack(context.Context, string) (apitype.UntypedDeployment, error)
	// ImportStack imports the specified deployment state into a pre-existing stack.
	// This can be combined with ExportStack to edit a stack's state (such as recovery from failed deployments).
	ImportStack(context.Context, string, apitype.UntypedDeployment) error
	// StackOutputs gets the current set of Stack outputs from the last Stack.Up().
	StackOutputs(context.Context, string) (OutputMap, error)
	// Install installs the workspace's dependencies.
	Install(context.Context, *InstallOptions) error
}

// ConfigValue is a configuration value used by a Pulumi program.
// Allows differentiating between secret and plaintext values by setting the `Secret` property.
type ConfigValue struct {
	Value  string
	Secret bool
}

// ConfigOptions is a configuration option used by a Pulumi program.
type ConfigOptions struct {
	// Allows to use the path flag while getting/setting the configuration.
	Path bool
	// Allows to use the config file flag while getting/setting the configuration.
	ConfigFile string
}

// GetAllConfigOptions is a configuration option used by a Pulumi program.
type GetAllConfigOptions struct {
	// Allows to use the config file flag while getting/setting the configuration.
	ConfigFile string
	// Allows to show secrets while getting the configuration.
	ShowSecrets bool
}

// ConfigMap is a map of ConfigValue used by Pulumi programs.
// Allows differentiating between secret and plaintext values.
type ConfigMap map[string]ConfigValue

// StackSummary is a description of a stack and its current status.
type StackSummary struct {
	Name             string `json:"name"`
	Current          bool   `json:"current"`
	LastUpdate       string `json:"lastUpdate,omitempty"`
	UpdateInProgress bool   `json:"updateInProgress"`
	ResourceCount    *int   `json:"resourceCount,omitempty"`
	URL              string `json:"url,omitempty"`
}

// Information about the token that was used to authenticate the current user. One (or none) of Team or Organization
// will be set, but not both.
type TokenInformation struct {
	Name         string `json:"name"`                   // The name of the token.
	Organization string `json:"organization,omitempty"` // If this was an organization token, the organization it was for.
	Team         string `json:"team,omitempty"`         // If this was a team token, the team it was for.
}

// WhoAmIResult contains detailed information about the currently logged-in Pulumi identity.
type WhoAmIResult struct {
	User             string            `json:"user"`
	Organizations    []string          `json:"organizations,omitempty"`
	URL              string            `json:"url"`
	TokenInformation *TokenInformation `json:"tokenInformation,omitempty"`
}

type ChangeSecretsProviderOptions struct {
	// NewPassphrase is the new passphrase when changing to a `passphrase` provider
	NewPassphrase *string
}

// InstallOptions are the options that can be passed for the Install command.
type InstallOptions struct {
	// Stdout is the optional writer to use for the output during installation.
	Stdout io.Writer
	// Stderr is the optional writer to use for the error output during installation.
	Stderr io.Writer
	// Use language version tools to setup the language runtime before installing the dependencies.
	// For Python this will use `pyenv` to install the Python version specified in a
	// `.python-version` file.
	UseLanguageVersionTools bool
	// Skip installing plugins
	NoPlugins bool
	// Skip installing dependencies
	NoDependencies bool
	// Reinstall plugins even if they already exist
	Reinstall bool
}
