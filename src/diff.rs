use crate::anchor;
use crate::file_io::read_file;
use thiserror::Error;

/// Check to see if and how an anchored file has changed since an anchor was created.
///
/// Get the difference between an existing anchor and an anchor built against the current state
/// of its file.
///
/// # Arguments
///
/// * `anchor` - The existing anchor to check.
///
/// # Returns
///
/// The first element of the returned tuple indicates whether any changes were found. The
/// second element is a vector of strings describing the diff (this may have contents even
/// if there is no actual difference).
/// 
/// # Errors
///
/// A std::error::Error describing any failure to construct a new Anchor.
pub fn get_anchor_diff(anchor: &anchor::Anchor) -> Result<(bool, Vec<String>), DiffError> {
    let full_text = read_file(anchor.file_path(), anchor.encoding())?;

    let context = anchor::Context::from_text(
        &full_text,
        anchor.context().offset(),
        anchor.context().topic().len(),
        anchor.context().width(),
    ).map_err(|err| DiffError::InvalidAnchor(err.to_string()))?;

    let new_anchor = anchor::Anchor::new(
        anchor.file_path(),
        context,
        anchor.metadata().clone(),
        anchor.encoding().clone(),
    ).map_err(|err| DiffError::InvalidAnchor(err.to_string()))?;

    let mut diff_strings: Vec<String> = Vec::new();

    let mut changed = false;

    for diff in diff::lines(
        anchor.context().full_text().as_str(),
        new_anchor.context().full_text().as_str(),
    ) {
        changed = match diff {
            diff::Result::Both(_, _) => changed,
            _ => true,
        };

        let diff_text = match diff {
            diff::Result::Left(l) => format!("-{}", l),
            diff::Result::Both(l, _) => format!(" {}", l),
            diff::Result::Right(r) => format!("+{}", r),
        };
        diff_strings.push(diff_text);
    }

    Ok((changed, diff_strings))
}

#[derive(Error, Debug)]
pub enum DiffError {
    #[error("Unable to create new anchor: {0}")]
    InvalidAnchor(String),

    #[error(transparent)]
    Io {
        #[from]
        source: std::io::Error,
    },

}

