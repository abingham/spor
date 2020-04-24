#[derive(Debug, PartialEq)]
pub enum AlignmentCell {
    Both { left: usize, right: usize }, // no gap; indices for both strings
    RightGap { left: usize },           // gap on right; index is for left string
    LeftGap { right: usize },           // gap on left; index is for right string
}

pub type Alignment = Vec<AlignmentCell>;

pub type Alignments = (f32, Vec<Alignment>);

pub trait Aligner {
    // Calculate the best alignments of sequences `a` and `b`.
    //
    // Arguments:
    //     a: The first of two sequences to align
    //     b: The second of two sequences to align
    //
    // Returns: A (score, alignments) tuple. `score` is the score that all of the
    //     `alignments` received. `alignments` is an iterable of `((index, index), .
    //     . .)` tuples describing the best (i.e. maximal and equally good)
    //     alignments. The first index in each pair is an index into `a` and the
    //     second is into `b`. Either (but not both) indices in a pair may be `None`
    //     indicating a gap in the corresponding sequence.
    fn align(&self, a: &str, b: &str) -> Alignments;
}
