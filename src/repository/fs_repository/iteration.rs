use std::path::{Path, PathBuf};

use super::fs_repository::FSRepository;
use super::serialization::read_anchor;
use crate::anchor::Anchor;

use crate::repository::AnchorId;

impl<'a> IntoIterator for &'a FSRepository {
    type Item = <RepositoryIterator<'a> as Iterator>::Item;
    type IntoIter = RepositoryIterator<'a>;

    fn into_iter(self) -> Self::IntoIter {
        RepositoryIterator::new(&self.spor_dir(), &self.root)
    }
}

pub struct RepositoryIterator<'a> {
    repo_root: &'a Path,
    anchor_files: Vec<(AnchorId, PathBuf)>,
}

impl<'a> RepositoryIterator<'a> {
    pub fn new(spor_dir: &PathBuf, repo_root: &'a Path) -> RepositoryIterator<'a> {
        let glob_path = spor_dir.join("**/*.yml");

        let pattern = glob_path
            .to_str()
            .expect(format!("Unable to stringify path {:?}. Invalid utf-8?", glob_path).as_str());

        let matches = glob::glob(pattern)
            .expect("Unexpected glob failure.")
            .filter_map(Result::ok)
            .map(|anchor_path| {
                anchor_path
                    .file_stem()
                    .and_then(|id| id.to_str())
                    .ok_or(())
                    .map(|id| (id.to_owned(), anchor_path.clone()))
            })
            .filter_map(Result::ok)
            .collect();

        RepositoryIterator {
            repo_root: repo_root,
            anchor_files: matches,
        }
    }
}

// TODO: What about a Stream of anchors? Isn't that the right thing to do in
// async land?

impl<'a> Iterator for RepositoryIterator<'a> {
    type Item = (AnchorId, Anchor);

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            let (anchor_id, anchor_path) = self.anchor_files.pop()?;
            let anchor_res =
                futures::executor::block_on(read_anchor(&anchor_path, &self.repo_root));
            match anchor_res {
                Ok(anchor) => return Some((anchor_id, anchor)),
                _ => (),
            };
        }
    }
}
