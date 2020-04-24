This is a script for demo-ing `spor`. It's based on the `follow-history` tool applied to a specific version of `anchor.rs`. 

0. Create history for anchor.rs:
```
get_history.py ../.. ../../src/anchor.rs history
```

1. Copy original version of `anchor.rs`
```
cp history/00-anchor.rs anchor.rs
```

2. Initialize spor repository
```
cargo run init
```

3. Create anchor
```
echo "{meta: data}" | cargo run add anchor.rs 46 20 10
```

Examine the anchor file.

4. Demonstrate `spor` commands
```
cargo run list anchor.rs
cargo run details <anchor id>
cargo run status
```

5. "edit" anchor.rs
```
cp history/01-anchor.rs anchor.rs
```

6. Show status and diff
```
cargo run status
cargo run diff <anchor id>
```

7. Update the anchor

Show the anchor in the editor so we can see it change.

```
cargo run update
```

We should see the anchor updated to match the new source.

8. Repeat edit/update cycle through version 05 

With this edit, we change the data type of the anchored thing, and we might
expect spor to fall over. But it updates correctly!

10. Continue "editing" through to number 10

Again, we see that the update at edit 10 works.
