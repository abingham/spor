pub trait Scorer {
    fn score(&self, a: char, b: char) -> f32;
    fn gap_penalty(&self, size: u32) -> f32;
}
