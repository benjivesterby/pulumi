// *** WARNING: this file was generated by test. ***
// *** Do not edit by hand unless you're certain you know what you are doing! ***

import * as pulumi from "@pulumi/pulumi";
import * as inputs from "../../types/input";
import * as outputs from "../../types/output";
import * as utilities from "../../utilities";

/**
 * A test for namespaces (mod 2)
 */
export interface TypArgs {
    mod1?: pulumi.Input<inputs.mod1.TypArgs>;
    val?: pulumi.Input<string>;
}
/**
 * typArgsProvideDefaults sets the appropriate defaults for TypArgs
 */
export function typArgsProvideDefaults(val: TypArgs): TypArgs {
    return {
        ...val,
        mod1: (val.mod1 ? pulumi.output(val.mod1).apply(inputs.mod1.typArgsProvideDefaults) : undefined),
        val: (val.val) ?? "mod2",
    };
}