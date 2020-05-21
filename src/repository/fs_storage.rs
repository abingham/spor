use std::path::PathBuf;

use crate::anchor::RelativeAnchor;

use crate::repository::{new_anchor_id, AnchorId, Storage, StorageError};

/// Filesystem-based storage
#[derive(Debug)]
pub struct FSStorage {
    /// The full path to the spor dir.
    pub spor_dir: PathBuf,
}

impl FSStorage {
    /// Absolute path to the data file for `anchor_id`.
    fn anchor_path(&self, anchor_id: &AnchorId) -> PathBuf {
        let file_name = format!("{}.yml", anchor_id);
        let path = self.spor_dir.join(file_name);
        assert!(path.is_absolute());
        path
    }
}

impl Storage for FSStorage {
    fn add(&self, anchor: &RelativeAnchor) -> Result<AnchorId, StorageError> {
        let anchor_id = new_anchor_id();
        let anchor_path = self.anchor_path(&anchor_id);

        let f = std::fs::OpenOptions::new()
            .create_new(true)
            .write(true)
            .open(anchor_path)?;

        serde_yaml::to_writer(f, anchor)
            .map_err(|err| StorageError::Other(err.to_string()))
            .map(|_| anchor_id)
    }

    fn update(&self, anchor_id: &AnchorId, anchor: &RelativeAnchor) -> Result<(), StorageError> {
        let anchor_path = self.anchor_path(anchor_id);

        let f = std::fs::OpenOptions::new()
            .truncate(true)
            .write(true)
            .open(anchor_path)
            .map_err(|err| match err.kind() {
                std::io::ErrorKind::NotFound => StorageError::BadId(anchor_id.clone()),
                _ => StorageError::from(err)
            })?;

        serde_yaml::to_writer(f, anchor)
            .map_err(|err| StorageError::Other(err.to_string()))
            .map(|_| ())
    }

    fn get(&self, anchor_id: &AnchorId) -> Result<RelativeAnchor, StorageError> {
        let anchor_path = self.anchor_path(anchor_id);

        let f = std::fs::OpenOptions::new().read(true).open(anchor_path) 
            .map_err(|err| match err.kind() {
                std::io::ErrorKind::NotFound => StorageError::BadId(anchor_id.clone()),
                _ => StorageError::from(err)
            })?;

        serde_yaml::from_reader(f)
            .map_err(|err| StorageError::Other(err.to_string()))
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
