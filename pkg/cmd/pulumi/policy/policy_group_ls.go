// Copyright 2016-2024, Pulumi Corporation.
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

package policy

import (
	"errors"
	"fmt"
	"strconv"

	"github.com/spf13/cobra"

	"github.com/pulumi/pulumi/pkg/v3/backend"
	"github.com/pulumi/pulumi/pkg/v3/backend/display"
	cmdBackend "github.com/pulumi/pulumi/pkg/v3/cmd/pulumi/backend"
	"github.com/pulumi/pulumi/pkg/v3/cmd/pulumi/ui"
	pkgWorkspace "github.com/pulumi/pulumi/pkg/v3/workspace"
	"github.com/pulumi/pulumi/sdk/v3/go/common/apitype"
	"github.com/pulumi/pulumi/sdk/v3/go/common/util/cmdutil"
	"github.com/pulumi/pulumi/sdk/v3/go/common/workspace"
)

func newPolicyGroupCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "group",
		Short: "Manage policy groups",
		Args:  cmdutil.NoArgs,
	}

	cmd.AddCommand(newPolicyGroupLsCmd())
	return cmd
}

func newPolicyGroupLsCmd() *cobra.Command {
	var jsonOut bool
	cmd := &cobra.Command{
		Use:   "ls [org-name]",
		Args:  cmdutil.MaximumNArgs(1),
		Short: "List all Policy Groups for a Pulumi organization",
		Long:  "List all Policy Groups for a Pulumi organization",
		RunE: func(cmd *cobra.Command, cliArgs []string) error {
			ctx := cmd.Context()

			// Try to read the current project
			ws := pkgWorkspace.Instance
			project, _, err := ws.ReadProject()
			if err != nil && !errors.Is(err, workspace.ErrProjectNotFound) {
				return err
			}

			// Get backend.
			b, err := cmdBackend.CurrentBackend(
				ctx, ws, cmdBackend.DefaultLoginManager, project,
				display.Options{Color: cmdutil.GetGlobalColorization()})
			if err != nil {
				return fmt.Errorf("failed to get current backend: %w", err)
			}

			// Get organization.
			var orgName string
			if len(cliArgs) > 0 {
				orgName = cliArgs[0]
			} else {
				orgName, _, _, err = b.CurrentUser()
				if err != nil {
					return err
				}
			}

			// Gather all Policy Groups for the organization.
			var (
				allPolicyGroups []apitype.PolicyGroupSummary
				inContToken     backend.ContinuationToken
			)
			for {
				resp, outContToken, err := b.ListPolicyGroups(ctx, orgName, inContToken)
				if err != nil {
					return err
				}

				allPolicyGroups = append(allPolicyGroups, resp.PolicyGroups...)

				if outContToken == nil {
					break
				}
				inContToken = outContToken
			}

			if jsonOut {
				return formatPolicyGroupsJSON(allPolicyGroups)
			}
			return formatPolicyGroupsConsole(allPolicyGroups)
		},
	}
	cmd.PersistentFlags().BoolVarP(
		&jsonOut, "json", "j", false, "Emit output as JSON")
	return cmd
}

func formatPolicyGroupsConsole(policyGroups []apitype.PolicyGroupSummary) error {
	// Header string and formatting options to align columns.
	headers := []string{"NAME", "DEFAULT", "ENABLED POLICY PACKS", "STACKS"}

	rows := []cmdutil.TableRow{}

	for _, group := range policyGroups {
		// Name column
		name := group.Name

		// Default column
		var defaultGroup string
		if group.IsOrgDefault {
			defaultGroup = "Y"
		} else {
			defaultGroup = "N"
		}

		// Number of enabled Policy Packs column
		numPolicyPacks := strconv.Itoa(group.NumEnabledPolicyPacks)

		// Number of stacks colum
		numStacks := strconv.Itoa(group.NumStacks)

		// Render the columns.
		columns := []string{name, defaultGroup, numPolicyPacks, numStacks}
		rows = append(rows, cmdutil.TableRow{Columns: columns})
	}
	ui.PrintTable(cmdutil.Table{
		Headers: headers,
		Rows:    rows,
	}, nil)
	return nil
}

// policyGroupsJSON is the shape of the --json output of this command. When --json is passed, we print an array
// of policyGroupsJSON objects.  While we can add fields to this structure in the future, we should not change
// existing fields.
type policyGroupsJSON struct {
	Name           string `json:"name"`
	Default        bool   `json:"default"`
	NumPolicyPacks int    `json:"numPolicyPacks"`
	NumStacks      int    `json:"numStacks"`
}

func formatPolicyGroupsJSON(policyGroups []apitype.PolicyGroupSummary) error {
	output := make([]policyGroupsJSON, len(policyGroups))
	for i, group := range policyGroups {
		output[i] = policyGroupsJSON{
			Name:           group.Name,
			Default:        group.IsOrgDefault,
			NumPolicyPacks: group.NumEnabledPolicyPacks,
			NumStacks:      group.NumStacks,
		}
	}
	return ui.PrintJSON(output)
}
