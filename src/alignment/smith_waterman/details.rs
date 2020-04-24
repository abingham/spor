use super::scorer::Scorer;
use crate::alignment::align::*;

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Direction {
    Diag,
    Up,
    Left,
}

type Directions = Vec<Direction>;

type ScoreMatrix = ndarray::Array2<f32>;
type TracebackMatrix = ndarray::Array2<Directions>;
pub type Index = (ndarray::Ix, ndarray::Ix);
type Traceback = Vec<Index>;

// Calculate the tracebacks for `traceback_matrix` starting at index `idx`.
//
// Note that tracebacks are in reverse. The first element in the traceback is
// the "biggest" index in the traceback, and they work their way backward
// through the strings being aligned.
pub fn tracebacks(traceback_matrix: &TracebackMatrix, idx: Index) -> Vec<Traceback> {
    let directions = traceback_matrix.get(idx).expect("index is invalid");
    if directions.is_empty() {
        vec![vec![]]
    } else {
        let mut tbs: Vec<Traceback> = Vec::new();

        let (row, col) = idx;

        for dir in directions {
            let tail_idx = match dir {
                Direction::Up => (row - 1, col),
                Direction::Diag => (row - 1, col - 1),
                Direction::Left => (row, col - 1),
            };

            let tails = tracebacks(traceback_matrix, tail_idx);

            for tail in tails {
                let mut tb = vec![idx];
                tb.extend(tail);
                tbs.push(tb);
            }
        }

        tbs
    }
}

pub fn build_score_matrix(a: &str, b: &str, scorer: &dyn Scorer) -> (ScoreMatrix, TracebackMatrix) {
    let mut score_matrix = ScoreMatrix::zeros((a.len() + 1, b.len() + 1));

    let mut traceback_matrix =
        TracebackMatrix::from_elem((a.len() + 1, b.len() + 1), Directions::new());

    for (row, a_char) in a.chars().enumerate() {
        for (col, b_char) in b.chars().enumerate() {
            let row = row + 1;
            let col = col + 1;

            let scores = [
                (
                    Direction::Diag,
                    score_matrix[(row - 1, col - 1)] + scorer.score(a_char, b_char),
                ),
                (
                    Direction::Up,
                    score_matrix[(row - 1, col)] - scorer.gap_penalty(1),
                ),
                (
                    Direction::Left,
                    score_matrix[(row, col - 1)] - scorer.gap_penalty(1),
                ),
            ];

            let max_score = scores
                .iter()
                .max_by_key(|n| ordered_float::OrderedFloat(n.1))
                .unwrap()
                .1;

            let directions: Vec<Direction> = scores
                .iter()
                .filter(|n| n.1 == max_score)
                .map(|n| n.0)
                .collect();

            if max_score > 0.0 {
                score_matrix[(row, col)] = max_score;
                traceback_matrix[(row, col)].extend(directions);
            }
        }
    }

    (score_matrix, traceback_matrix)
}

// Convert a traceback (i.e. as returned by `tracebacks()`) into an alignment
// (i.e. as returned by `align`).
//
// Arguments:
//   tb: A traceback.
//   a: the sequence defining the rows in the traceback matrix.
//   b: the sequence defining the columns in the traceback matrix.
//
// Returns: An iterable of (index, index) tupless where ether (but not both)
//   tuples can be `None`.
pub fn traceback_to_alignment(traceback: &Traceback) -> Result<Alignment, String> {
    if traceback.is_empty() {
        return Result::Ok(Alignment::new());
    }

    // We subtract 1 from the indices here because we're translating from the
    // alignment matrix space (which has one extra row and column) to the space
    // of the input sequences.
    let mut traceback: Traceback = traceback.iter().map(|(i1, i2)| (i1 - 1, i2 - 1)).collect();
    traceback.reverse();

    let mut alignment = Alignment::new();

    // The first element in the traceback is always included.
    alignment.push(AlignmentCell::Both {
        left: traceback[0].0,
        right: traceback[0].1,
    });

    // Now compare adjacent traceback entries to see how they changed.
    for ((curr_a, curr_b), (next_a, next_b)) in traceback.iter().zip(traceback.iter().skip(1)) {
        if *next_a == curr_a + 1 {
            if *next_b == curr_b + 1 {
                alignment.push(AlignmentCell::Both {
                    left: *next_a,
                    right: *next_b,
                });
            } else {
                if next_b != curr_b {
                    return Result::Err(format!("Invalid traceback: {:?}", traceback));
                }

                alignment.push(AlignmentCell::RightGap { left: *next_a });
            }
        } else {
            if next_a != curr_a {
                return Result::Err(format!("Invalid traceback: {:?}", traceback));
            }

            alignment.push(AlignmentCell::LeftGap { right: *next_b });
        }
    }

    Result::Ok(alignment)
}

#[cfg(test)]
mod tests {
    use super::super::simple_scorer::SimpleScorer;
    use super::*;

    const INPUT1: &str = "GGTTGACTA";
    const INPUT2: &str = "TGTTACGG";

    #[test]
    fn canned_tracebacks() {
        let (score_matrix, traceback_matrix) =
            build_score_matrix(INPUT1, INPUT2, &SimpleScorer::default());

        let max_idx = score_matrix
            .indexed_iter()
            .max_by_key(|n| ordered_float::OrderedFloat(*n.1))
            .unwrap()
            .0;

        let tbs = tracebacks(&traceback_matrix, max_idx);
        assert_eq!(tbs.len(), 1);

        let expected = [(7, 6), (6, 5), (5, 4), (4, 4), (3, 3), (2, 2)];

        assert_eq!(tbs[0], expected);
    }

    #[test]
    fn canned_score_matrix() {
        let expected = ndarray::Array::from_shape_vec(
            (10, 9),
            vec![
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1, 0, 0, 0, 3, 3, 0, 0, 3, 1, 0, 0, 0, 3, 6, 0,
                3, 1, 6, 4, 2, 0, 1, 4, 0, 3, 1, 4, 9, 7, 5, 3, 2, 0, 1, 6, 4, 7, 6, 4, 8, 6, 0, 0,
                4, 3, 5, 10, 8, 6, 5, 0, 0, 2, 1, 3, 8, 13, 11, 9, 0, 3, 1, 5, 4, 6, 11, 10, 8, 0,
                1, 0, 3, 2, 7, 9, 8, 7,
            ]
            .iter()
            .map(|n| *n as f32)
            .collect(),
        )
        .unwrap();

        let (score_matrix, _) = build_score_matrix(INPUT1, INPUT2, &SimpleScorer::default());

        assert_eq!(expected, score_matrix);
    }
}
