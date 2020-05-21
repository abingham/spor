use super::super::align::{Aligner, Alignments};
use super::details::{build_score_matrix, traceback_to_alignment, tracebacks, Index};
use super::scorer::Scorer;

/// Performs string alignment using the Smith-Waterman algorithm.
pub struct SmithWaterman<T>
where
    T: Scorer,
{
    scorer: T,
}

impl<T: Scorer> SmithWaterman<T> {
    pub fn new(scorer: T) -> SmithWaterman<T>
    where
        T: Scorer,
    {
        SmithWaterman { scorer: scorer }
    }
}

impl<T: Scorer> Aligner for SmithWaterman<T> {
    fn align(&self, a: &str, b: &str) -> Alignments {
        let (score_matrix, tb_matrix) = build_score_matrix(a, b, &self.scorer);
        let max_score = score_matrix
            .iter()
            .max_by_key(|&n| ordered_float::OrderedFloat(*n))
            .expect("alignment is not possible with empty strings.");

        let max_indices: Vec<Index> = score_matrix
            .indexed_iter()
            .filter(|(_, score)| *score == max_score)
            .map(|(index, _)| index)
            .collect();

        let mut alignments = vec![];
        for index in max_indices {
            for traceback in tracebacks(&tb_matrix, index) {
                match traceback_to_alignment(&traceback) {
                    Ok(alignment) => alignments.push(alignment),
                    Err(msg) => panic!(msg),
                }
            }
        }
        Alignments::new(*max_score, alignments)
    }
}

#[cfg(test)]
mod tests {
    use super::super::super::align::AlignmentCell;
    use super::super::simple_scorer::SimpleScorer;
    use super::*;

    const INPUT1: &str = "GGTTGACTA";
    const INPUT2: &str = "TGTTACGG";

    #[test]
    fn canned_alignment() {
        let alignments =
            SmithWaterman::<SimpleScorer>::new(SimpleScorer::default()).align(INPUT1, INPUT2);
        assert_eq!(alignments.score(), 13.0);
        assert_eq!(alignments.len(), 1);

        let expected = vec![
            AlignmentCell::Both { left: 1, right: 1 },
            AlignmentCell::Both { left: 2, right: 2 },
            AlignmentCell::Both { left: 3, right: 3 },
            AlignmentCell::RightGap { left: 4 },
            AlignmentCell::Both { left: 5, right: 4 },
            AlignmentCell::Both { left: 6, right: 5 },
        ];

        assert_eq!(*alignments.iter().next().unwrap(), expected);
    }
}
