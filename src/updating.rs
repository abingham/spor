use thiserror::Error;

use crate::alignment::align::{Aligner, AlignmentCell};
use crate::anchor::{Anchor, Context};
use crate::file_io::read_file;

/// Update an anchor based on the current contents of its source file.
pub fn update(anchor: &Anchor, align: &dyn Aligner) -> Result<Anchor, UpdateError> {
    let contents = read_file(anchor.file_path(), anchor.encoding())?;
    _update(anchor, &contents, align)
}

/// The main update implementation.
///
/// This takes in a reader of the anchored text, making it easier to test
/// (since it can work without the file actually existing).
fn _update(anchor: &Anchor, full_text: &str, aligner: &dyn Aligner) -> Result<Anchor, UpdateError> {
    let ctxt = anchor.context();

    let alignments = aligner.align(&ctxt.full_text(), &full_text);

    let alignment = match alignments.iter().next() {
        Some(a) => Ok(a),
        None => Err(UpdateError::NoAlignments),
    }?;

    let anchor_offset = (ctxt.offset() as usize) - ctxt.before().len();

    // Determine the new location of the topic in the modified source
    let source_indices: Vec<usize> = alignment
        .into_iter()
        // Look for all cells in the alignment where both sides contribute.
        .filter_map(|a| match a {
            AlignmentCell::Both { left: l, right: r } => Some((l, r)),
            _ => None,
        })
        // Keep only the cells where the anchor index is in the topic (i.e. no
        // in the before or after part of the context)
        .filter(|(a_idx, _)| index_in_topic(*a_idx + anchor_offset, &anchor))
        // From those cells, extract the index in the modified source.
        .map(|(_, s_idx)| *s_idx)
        .collect();

    let new_topic_offset = match source_indices.first() {
        Some(index) => Ok(index),
        None => Err(UpdateError::InvalidAnchor(String::from(
            "Can not match context to new source.",
        ))),
    }?;

    // Given the new topic offset and size, we can create a new context and
    // anchor.
    Context::from_text(
        full_text,
        *new_topic_offset,
        source_indices.len(),
        anchor.context().width(),
    )
    .map_err(|err| UpdateError::InvalidAnchor(err.to_string()))
    .and_then(|context| {
        Anchor::new(
            anchor.file_path(),
            context,
            anchor.metadata().clone(),
            anchor.encoding().clone(),
        )
        .map_err(|err| UpdateError::InvalidAnchor(err.to_string()))
    })
}

#[derive(Error, Debug)]
pub enum UpdateError {
    #[error("No alignment could be found in update")]
    NoAlignments,

    #[error("Unable to create new anchor: {0}")]
    InvalidAnchor(String),

    #[error(transparent)]
    Io {
        #[from]
        source: std::io::Error,
    },
}

// Determines if an index is in the topic of an anchor
fn index_in_topic(index: usize, anchor: &Anchor) -> bool {
    (index >= anchor.context().offset() as usize)
        && (index < anchor.context().offset() as usize + anchor.context().topic().len())
}

#[cfg(test)]
mod tests {
    use super::super::alignment::smith_waterman::{SimpleScorer, SmithWaterman};
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn successful_update() {
        let initial_text = "asdf";
        let final_text = "qwer\nasdf";

        let context = Context::from_text(initial_text, 0, 4, 3).unwrap();

        let metadata = serde_yaml::from_str("foo: bar").unwrap();

        let anchor = Anchor::new(
            &PathBuf::from("/foo/bar"),
            context,
            metadata,
            "utf-8".to_string(),
        )
        .unwrap();

        let updated_anchor = _update(
            &anchor,
            final_text,
            &SmithWaterman::<SimpleScorer>::new(SimpleScorer::default()),
        )
        .unwrap();

        assert_eq!(updated_anchor.context().offset(), 5);
    }
}
