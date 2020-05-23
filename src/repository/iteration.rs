use super::Repository;
use crate::anchor::Anchor;

use crate::repository::AnchorId;

impl IntoIterator for Repository {
    type Item = <Iterator as std::iter::Iterator>::Item;
    type IntoIter = Iterator;

    fn into_iter(self) -> Self::IntoIter {
        Iterator::new(self)
    }
}

pub struct Iterator {
    repo: Repository,
    anchor_ids: Vec<AnchorId>,
}

impl Iterator {
    pub fn new(repo: Repository) -> Iterator {
        Iterator {
            anchor_ids: repo.storage.all_anchor_ids(),
            repo: repo,
        }
    }
}

impl std::iter::Iterator for Iterator {
    type Item = (AnchorId, Anchor);

    fn next(&mut self) -> Option<Self::Item> {
        loop {
            let anchor_id = self.anchor_ids.pop()?;
            match self.repo.get(&anchor_id) {
                Ok(anchor) => return Some((anchor_id, anchor)),
                _ => (),
            }
        }
    }
}

// impl<'a> IntoIterator for &'a Repository {
//     type Item = <RefIterator<'a> as std::iter::Iterator>::Item;
//     type IntoIter = RefIterator<'a>;

//     fn into_iter(self) -> Self::IntoIter {
//         RefIterator::new(self)
//     }
// }

// pub struct RefIterator<'a> {
//     repo: &'a Repository,
//     anchor_ids: Vec<AnchorId>,
// }

// impl<'a> RefIterator<'a> {
//     pub fn new(repo: &'a Repository) -> RefIterator<'a> {
//         RefIterator {
//             anchor_ids: repo.storage.all_anchor_ids(),
//             repo: repo,
//         }
//     }
// }

// impl<'a> std::iter::Iterator for RefIterator<'a> {
//     type Item = (AnchorId, Anchor);

//     fn next(&mut self) -> Option<Self::Item> {
//         loop {
//             let anchor_id = self.anchor_ids.pop()?;
//             match self.repo.get(&anchor_id) {
//                 Ok(anchor) => return Some((anchor_id, anchor)),
//                 _ => (),
//             }
//         }
//     }
// }

