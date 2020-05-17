mod fs_storage;
mod iteration;

use crate::anchor::{Anchor, RelativeAnchor};
use fs_storage::FSStorage;
use std::fs::DirBuilder;
use std::io;
use std::path::{Path, PathBuf};

pub type AnchorId = String;

pub fn new_anchor_id() -> AnchorId {
    format!("{}", uuid::Uuid::new_v4())
}

/// The top-level container of anchor data.
///
/// A Repository comprises configuration data and a `Storage` implementation which manages the actual persistence of
/// anchors.
pub struct Repository {
    repo_dir: PathBuf,
    pub(self) storage: Box<dyn Storage>,
    // TODO: Eventually this will hold the repository config as well.
}

impl Repository {
    pub fn add(&self, anchor: Anchor) -> Result<AnchorId, String> {
        anchor
            .file_path()
            .strip_prefix(&self.repo_dir)
            .map_err(|err| err.to_string())
            .and_then(|rel_path| {
                // TODO: Can we create an "into" between anchor types that cuts down on copies?
                RelativeAnchor::new(
                    rel_path,
                    anchor.context().clone(),
                    anchor.metadata().clone(),
                    anchor.encoding().clone(),
                ).map_err(|err| err.to_string())
            })
            .and_then(|rel_anchor| self.storage.add(&rel_anchor))
    }

    pub fn update(&self, anchor_id: AnchorId, anchor: &Anchor) -> Result<(), String> {
        anchor
            .file_path()
            .strip_prefix(&self.repo_dir)
            .map_err(|err| err.to_string())
            .and_then(|rel_path| {
                // TODO: Can we create an "into" between anchor types that cuts down on copies?
                RelativeAnchor::new(
                    rel_path,
                    anchor.context().clone(),
                    anchor.metadata().clone(),
                    anchor.encoding().clone(),
                )
                .map_err(|err| err.to_string())
            })
            .and_then(|rel_anchor| self.storage.update(anchor_id, &rel_anchor))
    }

    pub fn get(&self, anchor_id: &AnchorId) -> Result<Anchor, String> {
        self.storage.get(anchor_id).and_then(|rel_anchor| {
            let abs_path = self.repo_dir.join(rel_anchor.file_path());
            Anchor::new(
                &abs_path,
                rel_anchor.context().clone(),
                rel_anchor.metadata().clone(),
                rel_anchor.encoding().clone(),
            )
            .map_err(|err| err.to_string())
        })
    }
}

pub(super) trait Storage {
    fn add(&self, anchor: &RelativeAnchor) -> Result<AnchorId, String>;
    fn update(&self, anchor_id: AnchorId, anchor: &RelativeAnchor) -> Result<(), String>;
    fn get(&self, anchor_id: &AnchorId) -> Result<RelativeAnchor, String>;
    fn all_anchor_ids(&self) -> Vec<AnchorId>;

    // get by id
    // update
    // remove
    // iterate
    // items
}

/// Initialize a spor repository in `path` if one doesn't already exist.
pub fn initialize(path: &Path, spor_dir: Option<&Path>) -> io::Result<()> {
    let spor_dir = spor_dir.unwrap_or(Path::new(".spor"));

    let spor_path = path.join(spor_dir);

    if spor_path.exists() {
        Err(io::Error::new(
            io::ErrorKind::AlreadyExists,
            "spor directory already exists",
        ))
    } else {
        let mut builder = DirBuilder::new();
        builder.recursive(true);
        builder.create(spor_path)
    }
}

/// Find the repository directory for the file `path` and return a
/// `Repository` for it.
pub fn open(path: &Path, spor_dir: Option<&Path>) -> io::Result<Repository> {
    let spor_dir = PathBuf::from(spor_dir.unwrap_or(&PathBuf::from(".spor")));

    find_root_dir(path, &spor_dir).map(|repo_dir| {
        let spor_dir = repo_dir.join(spor_dir);
        assert!(
            spor_dir.exists(),
            "spor-dir not found after find_root_dir succeeded!"
        );

        let storage = FSStorage {
            spor_dir: spor_dir,
            repo_dir: repo_dir.clone(),
        };

        Repository {
            repo_dir: repo_dir,
            storage: Box::new(storage),
        }
    })
}

/// Search for a spor repo containing `path`.
///
/// This searches for `spor_dir` in directories dominating `path`. If a
/// directory containing `spor_dir` is found, then that directory is returned.
///
/// Returns: The dominating directory containing `spor_dir`.
fn find_root_dir(path: &Path, spor_dir: &Path) -> io::Result<PathBuf> {
    let ancestor = PathBuf::from(path).canonicalize().map(|p| {
        p.ancestors()
            .into_iter()
            .filter_map(|a| {
                let repo = a.join(spor_dir);
                if repo.exists() && repo.is_dir() {
                    Some(PathBuf::from(a))
                } else {
                    None
                }
            })
            .next()
    })?;

    match ancestor {
        None => Err(io::Error::new(
            io::ErrorKind::NotFound,
            "Unable to find root directory",
        )),
        Some(path) => Ok(path),
    }
}
