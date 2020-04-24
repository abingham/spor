This is a demo showing how anchors follow changes to a file.

The `get_history.py` script takes a thread of history for a file and puts each snapshot into a directory:

```
get_history.py rust_spor rust_spor/src/repository.py history
```

Then each stage of `repository.py`'s history will be in the `history` directory.
The idea is to then create an anchor for some part of the file and then use
`spor update` to move the anchor over the evolution of the file. We "evolve" the
file by copying new versions from its history into place. See the script for
more details.