use serde::{Deserialize, Serialize};
use std::cmp::max;
use thiserror::Error;

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Context {
    before: String,
    offset: usize,
    topic: String,
    after: String,
    width: usize,
}

impl Context {
    pub fn new(text: &str, offset: usize, width: usize, context_width: usize) -> Result<Context, ContextError> {
        let topic: String = text.chars().skip(offset).take(width).collect();

        if topic.len() < width {
            return Err(ContextError::DataError(String::from("Unable to read topic")));
        }

        // read before
        let before_offset = if context_width <= offset {
            max(0, offset - context_width)
        } else {
            0
        };
        let before_width = offset - before_offset;
        let before: String = text
            .chars()
            .skip(before_offset)
            .take(before_width)
            .collect();

        // read after
        let after_offset = offset + width;
        let after: String = text
            .chars()
            .skip(after_offset)
            .take(context_width)
            .collect();

        let context = Context {
            before: before,
            offset: offset,
            topic: topic,
            after: after,
            width: context_width,
        };

        Ok(context)
    }

    pub fn before(&self) -> &String {
        &self.before
    }

    pub fn offset(&self) -> usize {
        self.offset
    }

    pub fn topic(&self) -> &String {
        &self.topic
    }

    pub fn after(&self) -> &String {
        &self.after
    }

    pub fn width(&self) -> usize {
        self.width
    }

    pub fn full_text(self: &Context) -> String {
        format!("{}{}{}", self.before, self.topic, self.after)
    }
}

#[derive(Debug, Error)]
pub enum ContextError {
    #[error("{0}")]
    DataError(String)
}

#[cfg(test)]
mod tests {
    use super::*;

    mod context {
        use super::*;

        #[test]
        fn construct_context_with_topic_at_front_of_file() {
            Context::new("text", 0, 4, 3).unwrap();
        }
    }
}