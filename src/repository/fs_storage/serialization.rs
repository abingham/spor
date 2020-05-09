use async_std::io;
use async_std::io::prelude::*;
use std::path::{Path, PathBuf};

use crate::anchor::{Anchor, Context};

pub async fn write_anchor(anchor_path: &Path, anchor: &Anchor, repo_root: &Path) -> io::Result<()> {
    let mut m = serde_yaml::Mapping::new();
    let file_path = anchor.file_path().strip_prefix(repo_root).map_err(|_| {
        io::Error::new(
            io::ErrorKind::InvalidData,
            "Anchored file not within repository",
        )
    })?;

    let file_path = file_path.to_str().ok_or(io::Error::new(
        io::ErrorKind::InvalidData,
        "unable to serialize file path",
    ))?;

    m.insert(
        serde_yaml::Value::String("file_path".to_owned()),
        serde_yaml::Value::String(file_path.to_owned()),
    );

    m.insert(
        serde_yaml::Value::String("encoding".to_owned()),
        serde_yaml::Value::String(anchor.encoding().clone()),
    );

    m.insert(
        serde_yaml::Value::String("metadata".to_owned()),
        anchor.metadata().clone(),
    );

    m.insert(
        serde_yaml::Value::String("context".to_owned()),
        serde_yaml::to_value(anchor.context()).or(Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "unable to serialize context",
        )))?,
    );

    // NB: Serde doesn't do async yet, so we try to fake it here.
    match serde_yaml::to_vec(&m) {
        Err(info) => Err(io::Error::new(io::ErrorKind::InvalidData, info)),
        Ok(buffer) => {
            let mut f = async_std::fs::File::create(anchor_path).await?;
            f.write_all(&buffer).await?;
            Ok(())
        }
    }
}

pub(crate) async fn read_anchor(anchor_path: &Path, repo_root: &Path) -> io::Result<Anchor> {
    let mut buffer: Vec<u8> = vec![];
    let mut f = async_std::fs::File::open(anchor_path).await?;
    f.read_to_end(&mut buffer).await?;

    match serde_yaml::from_slice(&buffer) {
        Err(info) => return Err(io::Error::new(io::ErrorKind::InvalidData, info)),
        Ok(m) => {
            let m: serde_yaml::Mapping = m;

            let fp = m
                .get(&serde_yaml::Value::String("file_path".to_owned()))
                .and_then(|value| value.as_str())
                .map(|value| {
                    let mut path = PathBuf::new();
                    path.push(value);
                    path
                })
                .ok_or(io::Error::new(
                    io::ErrorKind::InvalidInput,
                    "Expected file_path field",
                ))?;

            let encoding = m
                .get(&serde_yaml::Value::String("encoding".to_owned()))
                .and_then(|v| v.as_str())
                .ok_or(io::Error::new(
                    io::ErrorKind::InvalidInput,
                    "expected encoding field",
                ))?;

            let metadata = m
                .get(&serde_yaml::Value::String("metadata".to_owned()))
                .ok_or(io::Error::new(
                    io::ErrorKind::InvalidInput,
                    "expected metadata field",
                ))?;

            let context = m
                .get(&serde_yaml::Value::String("context".to_owned()))
                .ok_or(io::Error::new(
                    io::ErrorKind::InvalidInput,
                    "expected context field",
                ))?;

            let context: Context = serde_yaml::from_value(context.clone()).map_err(|_e| {
                io::Error::new(io::ErrorKind::InvalidInput, "expected context field")
            })?;

            let a = Anchor::new(
                &repo_root.join(fp),
                context,
                metadata.clone(),
                encoding.to_owned(),
            )?;

            Ok(a)
        }
    }
}
