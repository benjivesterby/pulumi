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

import { CommandResult } from "./cmd";

/**
 * An error resulting from the invocation of a Pulumi command.
 *
 * @alpha
 */
export class CommandError extends Error {
    /** @internal */
    constructor(private commandResult: CommandResult) {
        super(commandResult.toString());
        this.name = "CommandError";
    }
}

/**
 * An error thrown when attempting to update a stack that is already being
 * updated.
 */
export class ConcurrentUpdateError extends CommandError {
    /** @internal */
    constructor(commandResult: CommandResult) {
        super(commandResult);
        this.name = "ConcurrentUpdateError";
    }
}

/**
 * An error thrown when attempting to select a stack that does not exist.
 */
export class StackNotFoundError extends CommandError {
    /** @internal */
    constructor(commandResult: CommandResult) {
        super(commandResult);
        this.name = "StackNotFoundError";
    }
}

/**
 * An error thrown when attempting to create a stack that already exists.
 */
export class StackAlreadyExistsError extends CommandError {
    /** @internal */
    constructor(commandResult: CommandResult) {
        super(commandResult);
        this.name = "StackAlreadyExistsError";
    }
}

const notFoundRegex = new RegExp("no stack named.*found");
const alreadyExistsRegex = new RegExp("stack.*already exists");
const conflictText = "[409] Conflict: Another update is currently in progress.";
const diyBackendConflictText = "the stack is currently locked by";

/**
 * @internal
 */
export function createCommandError(result: CommandResult): CommandError {
    const stderr = result.stderr;
    return notFoundRegex.test(stderr)
        ? new StackNotFoundError(result)
        : alreadyExistsRegex.test(stderr)
          ? new StackAlreadyExistsError(result)
          : stderr.indexOf(conflictText) >= 0
            ? new ConcurrentUpdateError(result)
            : stderr.indexOf(diyBackendConflictText) >= 0
              ? new ConcurrentUpdateError(result)
              : new CommandError(result);
}
