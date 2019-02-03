This is a project for taking the history
of changes for a file and seeing how an anchor
moves with the changes.

The `get_history.py` script takes a thread of history for a file and puts each snapshot into a directory:

```
get_history.py rust_spor rust_spor/src/repository.py history
```

Then each stage of `repository.py`'s history will be in the `history` directory. The idea is to then create an anchor for some part of the file and then use `spor update` to move the anchor over the evolution of the file.