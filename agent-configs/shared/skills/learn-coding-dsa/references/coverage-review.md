# Coverage review by problem type

Select sections that match the prompt. Treat these as questions to investigate, not additional API requirements. Derive assertions from the prompt or a clarifying-question answer stated in the starter. Keep expected results independent of the reference implementation.

## Concurrency and traversal

Check whether unfinished work can discover more work after other workers finish. Exercise duplicate discovery, cycles, worker failures, and the smallest supported worker count. Use events or barriers with bounded waits to establish ordering; avoid sleeps and speed assertions. For URLs, distinguish parsed-host matching from substring matching and test only the URL normalization the prompt requires.

## Stateful caches and persistence

Check capacity boundaries, access-order eviction, falsy values, repeated calls, and isolation from caller mutation. For persistence, distinguish incomplete final records from corrupt complete records. Exercise recovery after repeated evictions and failures before a result is acknowledged. Assert only the documented durability guarantee; a failed flush does not prove that bytes were rolled back.

## Files and transformation pipelines

Check no input files, identical names in separate directories, binary contents, and differences beyond a read-chunk boundary. Distinguish equal size or prefix from equal contents. For pipelines, exercise operation order, parameter-sensitive branches, empty pipelines, missing output subdirectories, and worker error propagation. Test spatial transformations with position-dependent pixels, not single-color images. Follow the prompt's rules for unreadable files and symlinks; avoid fixtures requiring platform-specific privileges.

## Numeric and distributed algorithms

Check ties, allowed numeric limits, empty partitions, one worker, and unequal partition sizes. Construct examples where combining local answers gives the wrong global answer. Check reported communication cost against the prompt's cost model; do not require an unstated algorithm.

## Parsers, tokenizers, and instruction execution

Check partial matches at the end of input, zero-valued identifiers, sentinel collisions, non-ASCII text, and advancing past empty tokens. For execution, distinguish the last executed instruction from a revisited jump target. Check the specified behavior when the instruction pointer moves before the first instruction or past the last one. Reject malformed input only when its behavior is defined.

## Call-stack samples and confirmation

Check:

- Recursion.
- Samples that change only inner frames, and samples that change every frame.
- Frames still open at end of input.
- Confirmation thresholds (samples needed before a frame counts) of one and of more than the sample count.
- With consecutive-sample confirmation: a gap resets the count, and unconfirmed frames do not emit end events.
- Equal or invalid timestamps, only under the stated ordering contract.
