// *** WARNING: this file was generated by pulumi-language-nodejs. ***
// *** Do not edit by hand unless you're certain you know what you are doing! ***

import * as pulumi from "@pulumi/pulumi";
import * as utilities from "./utilities";

// Export members:
export { HelloWorldArgs } from "./helloWorld";
export type HelloWorld = import("./helloWorld").HelloWorld;
export const HelloWorld: typeof import("./helloWorld").HelloWorld = null as any;
utilities.lazyLoad(exports, ["HelloWorld"], () => require("./helloWorld"));

export { HelloWorldComponentArgs } from "./helloWorldComponent";
export type HelloWorldComponent = import("./helloWorldComponent").HelloWorldComponent;
export const HelloWorldComponent: typeof import("./helloWorldComponent").HelloWorldComponent = null as any;
utilities.lazyLoad(exports, ["HelloWorldComponent"], () => require("./helloWorldComponent"));

export { ProviderArgs } from "./provider";
export type Provider = import("./provider").Provider;
export const Provider: typeof import("./provider").Provider = null as any;
utilities.lazyLoad(exports, ["Provider"], () => require("./provider"));


const _module = {
    version: utilities.getVersion(),
    construct: (name: string, type: string, urn: string): pulumi.Resource => {
        switch (type) {
            case "subpackage:index:HelloWorld":
                return new HelloWorld(name, <any>undefined, { urn })
            case "subpackage:index:HelloWorldComponent":
                return new HelloWorldComponent(name, <any>undefined, { urn })
            default:
                throw new Error(`unknown resource type ${type}`);
        }
    },
};
pulumi.runtime.registerResourceModule("subpackage", "index", _module)
pulumi.runtime.registerResourcePackage("subpackage", {
    version: utilities.getVersion(),
    constructProvider: (name: string, type: string, urn: string): pulumi.ProviderResource => {
        if (type !== "pulumi:providers:subpackage") {
            throw new Error(`unknown provider type ${type}`);
        }
        return new Provider(name, <any>undefined, { urn });
    },
});
