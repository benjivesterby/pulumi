// Copyright 2016-2022, Pulumi Corporation.
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
"use strict";

import * as packageJson from "../../package.json";
import * as opentelemetry from "@opentelemetry/api";
import { Resource } from "@opentelemetry/resources";
import { BatchSpanProcessor, SimpleSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { ZipkinExporter } from "@opentelemetry/exporter-zipkin";
import { GrpcInstrumentation } from "@opentelemetry/instrumentation-grpc";
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
import { registerInstrumentations } from "@opentelemetry/instrumentation";
import * as log from "../../log";

let exporter: ZipkinExporter;
let rootSpan: opentelemetry.Span;

// serviceName is the name of this service in the Pulumi
// distributed system, and the name of the tracer we're using.
const serviceName = "nodejs-runtime";

// These are constants defined by the OpenTelemetry project.  We used to import
// @opentelemetry/semantic-conventions, but the package caused a big amount of flakes.
// See also: https://github.com/pulumi/pulumi/issues/17823
const ATTR_SERVICE_NAME = "service.name";
const ATTR_SERVICE_VERSION = "service.version";

// If the URL provided matches the default generated by the engine,
// we must transform it to be compatible with the OpenTelemetry Zipkin
// library.
function validateUrl(destination: string): boolean {
    if (destination.startsWith("tcp://127.0.0.1")) {
        // This URI is invalid because the OpenTelemetry expects
        // a Zipkin-compatible API. This URI is likely sent by the Engine's
        // AppDash server when the user specifies a file endpoint.
        // In this case, we send a warning that we can't support this URI
        // and refuse to enable tracing.
        log.warn(
            "Detected an incompatible tracing URI. Refusing to enable tracing for the NodeJS runtime. If you provided a file target with the --tracing flag, understand that the NodeJS runtime does not support sending trace information to files.",
        );
        return false;
    }
    return true;
}

/** @internal */
export function start(destinationUrl: string) {
    if (!validateUrl(destinationUrl)) {
        return;
    }
    // Set up gRPC auto-instrumentation.
    registerInstrumentations({
        instrumentations: [new GrpcInstrumentation()],
    });

    // Tag traces from this program with metadata about their source.
    const resource = Resource.default().merge(
        new Resource({
            [ATTR_SERVICE_NAME]: serviceName,
            [ATTR_SERVICE_VERSION]: packageJson.version,
        }),
    );

    /**
     * Taken from OpenTelemetry Examples (Apache 2 License):
     * https://github.com/open-telemetry/opentelemetry-js/blob/a8d39317b5daad727f2116ca314db0d1420ec488/examples/basic-tracer-node/index.js
     * Initialize the OpenTelemetry APIs to use the BatchTracerProvider bindings.
     *
     * A "tracer provider" is a factory for tracers. By registering the provider,
     * we allow tracers of the given type to be globally contructed.
     * As a result, when you call API methods like
     * `opentelemetry.trace.getTracer`, the tracer is generated via the tracer provder
     * registered here.
     */

    // Create a new tracer provider, acting as a factory for tracers.
    const provider = new NodeTracerProvider({
        resource: resource,
    });

    // Configure span processor to send spans to the exporter
    log.debug(`Registering tracing url: ${destinationUrl}`);
    exporter = new ZipkinExporter({ url: destinationUrl, serviceName });
    provider.addSpanProcessor(new SimpleSpanProcessor(exporter));

    provider.register();
    const tracer = opentelemetry.trace.getTracer("nodejs-runtime");
    // Create a root span, which must be closed.
    rootSpan = tracer.startSpan("nodejs-runtime-root");
}

/** @internal */
export function stop() {
    // If rootSpan is null, the URI provided was invalid,
    // so tracing was never enabled.
    if (rootSpan != null) {
        log.debug("Shutting down tracer.");
        // Always close the root span.
        rootSpan.end();
    }
    // Do not bother stopping the tracing exporter. Because we use a
    // SimpleSpanProcessor, it eagerly sends spans.
}

/** @internal */
export function newSpan(name: string): opentelemetry.Span {
    const tracer = opentelemetry.trace.getTracer(serviceName);
    const parentSpan = opentelemetry.trace.getActiveSpan() ?? rootSpan;
    const activeCtx = opentelemetry.context.active();
    const ctx = opentelemetry.trace.setSpan(activeCtx, parentSpan);
    const childSpan = tracer.startSpan(name, undefined, ctx);
    return childSpan;
}
