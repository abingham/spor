use crate::anchor::Anchor;
use async_trait::async_trait;

pub type AnchorId = String;

pub fn new_anchor_id() -> AnchorId {
    format!("{}", uuid::Uuid::new_v4())
}

#[async_trait]
pub trait Repository {
    async fn add(&self, anchor: Anchor) -> Result<AnchorId, String>;
    async fn update(&self, anchor_id: AnchorId, anchor: &Anchor) -> Result<(), String>;
    async fn get(&self, anchor_id: &AnchorId) -> Result<Option<Anchor>, String>;

    // get by id
    // update
    // remove
    // iterate
    // items
}
