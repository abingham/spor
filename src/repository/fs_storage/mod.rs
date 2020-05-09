mod serialization;

use std::io;
use std::path::PathBuf;
use async_trait::async_trait;

use serialization::{read_anchor, write_anchor};
use crate::anchor::Anchor;

use crate::repository::{new_anchor_id, AnchorId, Storage};

/// Filesystem-based storage
#[derive(Debug)]
pub struct FSStorage {
    /// The full path to the spor dir.
    pub spor_dir: PathBuf,

    // TODO: I would like it if storage didn't need to worry about the repo_root but was instead dealing with 
    // some form of anchor that had relative paths in them.

    /// The path to the repo root
    pub repo_dir: PathBuf,
}

impl FSStorage {
    // pub fn spor_dir(&self) -> PathBuf {
    //     self.root.join(&self.spor_dir)
    // }

    /// Absolute path to the data file for `anchor_id`.
    fn anchor_path(&self, anchor_id: &AnchorId) -> PathBuf {
        let file_name = format!("{}.yml", anchor_id);
        let path = self.spor_dir.join(file_name);
        assert!(path.is_absolute());
        path
    }
}

#[async_trait]
impl Storage for FSStorage {
    async fn add(&self, anchor: Anchor) -> Result<AnchorId, String> {
        let anchor_id = new_anchor_id();
        let anchor_path = self.anchor_path(&anchor_id);

        if anchor_path.exists() {
            return Err(format!("{:?} already exists", anchor_path));
        }

        if let Err(err) = write_anchor(&anchor_path, &anchor, &self.repo_dir).await {
            return Err(format!("{:?}", err));
        }

        Ok(anchor_id)
    }

    async fn update(&self, anchor_id: AnchorId, anchor: &Anchor) -> Result<(), String> {
        let anchor_path = self.anchor_path(&anchor_id);
        if !anchor_path.exists() {
            return Err(format!("{:?} does not exist", anchor_path));
        }

        match write_anchor(&anchor_path, &anchor, &self.repo_dir).await {
            Ok(_) => Ok(()),
            Err(err) => Err(format!("{:?}", err)),
        }
    }

    async fn get(&self, anchor_id: &AnchorId) -> Result<Option<Anchor>, String> {
        let path = self.anchor_path(anchor_id);
        match read_anchor(&path, &self.repo_dir).await {
            Err(err) => match err.kind() {
                io::ErrorKind::NotFound => Ok(None),
                _ => Err(format!("{:?}", err)),
            },
            Ok(anchor) => Ok(Some(anchor)),
        }
    }

    fn all_anchor_ids(&self) -> Vec<AnchorId> {
        let glob_path = self.spor_dir.join("**/*.yml");

        let pattern = glob_path
            .to_str()
            .expect(format!("Unable to stringify path {:?}. Invalid utf-8?", glob_path).as_str());

        glob::glob(pattern)
            .expect("Unexpected glob failure.")
            .filter_map(Result::ok)
            .filter_map(|anchor_path| {
                anchor_path
                    .file_stem()
                    .and_then(|id| id.to_str())
                    .map(|id| id.to_owned())
            })
            .collect()
    }
}

