use async_std::fs::DirBuilder;
use std::io;
use std::path::{Path, PathBuf};
use async_trait::async_trait;

use super::iteration::RepositoryIterator;
use super::serialization::{read_anchor, write_anchor};
use crate::anchor::Anchor;

use crate::repository::{new_anchor_id, AnchorId, Repository};

/// Filesystem-based repository
#[derive(Debug)]
pub struct FSRepository {
    pub root: PathBuf,
    spor_dir: PathBuf,
}

impl FSRepository {
    /// Find the repository directory for the file `path` and return a
    /// `Repository` for it.
    pub fn new(path: &Path, spor_dir: Option<&Path>) -> io::Result<FSRepository> {
        let spor_dir = PathBuf::from(spor_dir.unwrap_or(&PathBuf::from(".spor")));

        find_root_dir(path, &spor_dir).map(|root_dir| {
            assert!(
                root_dir.join(&spor_dir).exists(),
                "spor-dir not found after find_root_dir succeeded!"
            );

            FSRepository {
                root: root_dir,
                spor_dir: spor_dir,
            }
        })
    }

    pub fn spor_dir(&self) -> PathBuf {
        self.root.join(&self.spor_dir)
    }

    /// Absolute path to the data file for `anchor_id`.
    fn anchor_path(&self, anchor_id: &AnchorId) -> PathBuf {
        let file_name = format!("{}.yml", anchor_id);
        let path = self.spor_dir().join(file_name);
        assert!(path.is_absolute());
        path
    }

    pub fn iter(&self) -> RepositoryIterator {
        RepositoryIterator::new(&self.spor_dir(), &self.root)
    }
}

#[async_trait]
impl Repository for FSRepository {
    async fn add(&self, anchor: Anchor) -> Result<AnchorId, String> {
        let anchor_id = new_anchor_id();
        let anchor_path = self.anchor_path(&anchor_id);

        if anchor_path.exists() {
            return Err(format!("{:?} already exists", anchor_path));
        }

        if let Err(err) = write_anchor(&anchor_path, &anchor, &self.root).await {
            return Err(format!("{:?}", err));
        }

        Ok(anchor_id)
    }

    async fn update(&self, anchor_id: AnchorId, anchor: &Anchor) -> Result<(), String> {
        let anchor_path = self.anchor_path(&anchor_id);
        if !anchor_path.exists() {
            return Err(format!("{:?} does not exist", anchor_path));
        }

        match write_anchor(&anchor_path, &anchor, &self.root).await {
            Ok(_) => Ok(()),
            Err(err) => Err(format!("{:?}", err)),
        }
    }

    async fn get(&self, anchor_id: &AnchorId) -> Result<Option<Anchor>, String> {
        let path = self.anchor_path(anchor_id);
        match read_anchor(&path, &self.root).await {
            Err(err) => match err.kind() {
                io::ErrorKind::NotFound => Ok(None),
                _ => Err(format!("{:?}", err)),
            },
            Ok(anchor) => Ok(Some(anchor)),
        }
    }
}

/// Initialize a spor repository in `path` if one doesn't already exist.
pub async fn initialize(path: &Path, spor_dir: Option<&Path>) -> io::Result<()> {
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
        builder.create(spor_path).await
    }
}

/// Search for a spor repo containing `path`.
///
/// This searches for `spor_dir` in directories dominating `path`. If a
/// directory containing `spor_dir` is found, then that directory is returned.
///
/// Returns: The dominating directory containing `spor_dir`.
fn find_root_dir(path: &Path, spor_dir: &Path) -> io::Result<PathBuf> {
    PathBuf::from(path)
        .canonicalize()
        .map(|p| {
            p.ancestors()
                .into_iter()
                .filter_map(|a| {
                    let repo = a.join(spor_dir);
                    if repo.exists() && repo.is_dir() {
                        Some(PathBuf::from(a))
                    }
                    else {
                        None
                    }
                })
                .next()
        })
        .map(|a| PathBuf::from(a.unwrap()))
}

