use super::Repository;
use crate::anchor::Anchor;

use crate::repository::AnchorId;

impl<'a> IntoIterator for &'a Repository {
    type Item = <Iterator<'a> as std::iter::Iterator>::Item;
    type IntoIter = Iterator<'a>;

    fn into_iter(self) -> Self::IntoIter {
        Iterator::new(self)
    }
}

pub struct Iterator<'a> {
    repo: &'a Repository,
    anchor_ids: Vec<AnchorId>,
}

impl<'a> Iterator<'a> {
    pub fn new(repo: &'a Repository) -> Iterator<'a> {
        Iterator {
            repo: repo,
            anchor_ids: repo.storage.all_anchor_ids(),
        }
    }
}

// TODO: What about a Stream of anchors? Isn't that the right thing to do in
// async land?

impl<'a> std::iter::Iterator for Iterator<'a> {
    type Item = (AnchorId, Anchor);

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            let anchor_id = self.anchor_ids.pop()?;
            let anchor_res = futures::executor::block_on(self.repo.get(&anchor_id));
            match anchor_res {
                Ok(Some(anchor)) => return Some((anchor_id, anchor)),
                _ => (),
            }
        }
    }
}
