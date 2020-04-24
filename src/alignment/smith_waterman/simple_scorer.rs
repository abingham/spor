use crate::alignment::smith_waterman::Scorer;

/// Simple scoring strategy for Smith-Waterman.
///
/// The base-score determines the score for matching tokens; the negative is used for mismatches. The gap-penalty is
/// multiplied by the length of the gap.
pub struct SimpleScorer {
    base_score: f32,
    base_gap_penalty: f32,
}

impl SimpleScorer {
    pub fn new(base_score: f32, base_gap_penalty: f32) -> SimpleScorer {
        SimpleScorer {
            base_score: base_score,
            base_gap_penalty: base_gap_penalty,
        }
    }

    pub fn default() -> SimpleScorer {
        SimpleScorer::new(3.0, 2.0)
    }
}

impl Scorer for SimpleScorer {
    // A standard scoring function
    fn score(&self, a: char, b: char) -> f32 {
        if a == b {
            self.base_score
        } else {
            self.base_score * -1.0
        }
    }

    // A standard gap-penalty function
    fn gap_penalty(&self, gap: u32) -> f32 {
        if gap == 1 {
            self.base_gap_penalty
        } else {
            (gap as f32) * self.gap_penalty(1)
        }
    }
}
