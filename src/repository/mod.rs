mod fs_storage;
mod iteration;

use crate::anchor::Anchor;
use async_trait::async_trait;
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
    pub(self) storage: Box<dyn Storage>, 
    // TODO: Eventually this will hold the repository config as well.
}

impl Repository {
    pub async fn add(&self, anchor: Anchor) -> Result<AnchorId, String> {
        self.storage.add(anchor).await
    }

    pub async fn update(&self, anchor_id: AnchorId, anchor: &Anchor) -> Result<(), String> {
        self.storage.update(anchor_id, anchor).await
    }

    pub async fn get(&self, anchor_id: &AnchorId) -> Result<Option<Anchor>, String> {
        self.storage.get(anchor_id).await
    }
}

#[async_trait]
pub(super) trait Storage {
    async fn add(&self, anchor: Anchor) -> Result<AnchorId, String>;
    async fn update(&self, anchor_id: AnchorId, anchor: &Anchor) -> Result<(), String>;
    async fn get(&self, anchor_id: &AnchorId) -> Result<Option<Anchor>, String>;
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

    find_root_dir(path, &spor_dir).map(|root_dir| {
        let spor_dir = root_dir.join(spor_dir);
        assert!(
            spor_dir.exists(),
            "spor-dir not found after find_root_dir succeeded!"
        );

        let storage = FSStorage {
            spor_dir: spor_dir,
            repo_dir: root_dir,
        };

        Repository {
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
