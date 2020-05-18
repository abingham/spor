use std::path::{Path, PathBuf};
use serde::{Serialize, Deserialize};
use std::marker::PhantomData;

mod check_path;
mod context;

use check_path::CheckPath;
pub use context::Context;

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Anchor_<PathType: CheckPath> {
    file_path: PathBuf,
    encoding: String,
    context: Context,
    metadata: serde_yaml::Value,
    check_path: PhantomData<PathType>
}


impl<PathType: CheckPath> Anchor_<PathType> {
    pub fn new(
        file_path: &Path,
        context: Context,
        metadata: serde_yaml::Value,
        encoding: String,
    ) -> Result<Anchor_<PathType>, String> {
        if let Some(msg) = PathType::check_path(file_path) {
            return Err(msg);
        }

        let anchor = Anchor_::<PathType> {
            file_path: PathBuf::from(file_path),
            encoding: encoding,
            context: context,
            metadata: metadata,
            check_path: PhantomData
        };

        Ok(anchor)
    }

    pub fn file_path(&self) -> &PathBuf {
        return &self.file_path;
    }

    pub fn encoding(&self) -> &String {
        return &self.encoding;
    }

    pub fn context(&self) -> &Context {
        return &self.context;
    }

    pub fn metadata(&self) -> &serde_yaml::Value {
        return &self.metadata;
    }
}

pub type Anchor = Anchor_::<check_path::AbsolutePath>;
pub type RelativeAnchor = Anchor_::<check_path::RelativePath>;

