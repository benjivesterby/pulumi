// *** WARNING: this file was generated by test. ***
// *** Do not edit by hand unless you're certain you know what you are doing! ***

using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Threading.Tasks;
using Pulumi.Serialization;

namespace Pulumi.Std.Outputs
{

    [OutputType]
    public sealed class AnotherCustomResult
    {
        public readonly string? Value;

        [OutputConstructor]
        private AnotherCustomResult(string? value)
        {
            Value = value;
        }
    }
}
