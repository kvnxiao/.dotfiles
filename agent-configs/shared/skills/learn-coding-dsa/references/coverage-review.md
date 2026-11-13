# Coverage review by problem type

Select sections that match the prompt. Treat these as questions to investigate, not additional API requirements. Derive assertions from the prompt or a contract assumption stated in the starter. Keep expected results independent of the reference implementation.

## Concurrency and traversal

Check whether unfinished work can discover more work after other workers finish. Exercise duplicate discovery, cycles, worker failures, and the smallest supported worker count. Use events or barriers with bounded waits to establish ordering; avoid sleeps and speed assertions. For URLs, distinguish parsed-host matching from substring matching and test only the required normalization.

## Stateful caches and persistence

Check capacity boundaries, access-order eviction, falsy values, repeated calls, and isolation from caller mutation. For persistence, distinguish incomplete final records from corrupt complete records. Exercise recovery after repeated evictions and failures before a result is acknowledged. Assert only the documented durability guarantee; a failed flush does not prove that bytes were rolled back.

## Files and transformation pipelines

Check empty worksets, identical names in separate directories, binary contents, and differences beyond a read-chunk boundary. Distinguish equal size or prefix from equal contents. For pipelines, exercise operation order, parameter-sensitive branches, empty pipelines, nested destinations, and worker error propagation. Use discriminating pixel values rather than uniform images when testing spatial transformations. Respect the documented policy for unreadable files and symlinks; avoid fixtures requiring platform-specific privileges.

## Numeric and distributed algorithms

Check ties, allowed numeric limits, empty partitions, one worker, and unequal partition sizes. Construct examples where combining local answers gives the wrong global answer. Validate cost accounting against the stated communication model without prescribing an unstated algorithm.

## Parsers, tokenizers, and instruction execution

Check partial matches at the end, zero-valued identifiers, sentinel collisions, Unicode units, and progress when empty tokens exist. For execution, distinguish the last executed instruction from a repeated target. Check the specified behavior when the instruction pointer moves before the first instruction or past the last one. Reject malformed input only when its behavior is defined.

## Stack histories and incremental confirmation

Check recursion by depth, preserved prefixes, replacement of an entire suffix, and live frames at end of input. Exercise confirmation thresholds of one and more than the available observations. When confirmation requires consecutive samples, check that a missing frame resets its count and unconfirmed frames do not emit closing events. Check equal or invalid timestamps only under the stated ordering contract.
