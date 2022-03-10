//! Support for ensuring that paths are absolute or relative.
//! 
//! This is an implementation detail that allows us to require Anchors
//! to carry absolute paths when being used in the API, but be stored
//! as relative paths (i.e. so that repositories can be moved around).

use std::path::Path;

/// Trait for checking if a path meets some criteria.
pub trait CheckPath {
    /// Checks if `path` meets the expected criteria.
    /// 
    /// Returns `None` if `path` meets the criteria, or an error
    /// message otherwise.
    fn check_path(path: &Path) -> Option<String>;
}

/// CheckPath marker struct for relative paths.
pub struct RelativePath {}

/// CheckPath implementation that checks if paths are relative.
impl CheckPath for RelativePath {
    /// Returns `None` if `path` is relative, or an error message
    /// otherwise.
    fn check_path(path: &Path) -> Option<String> {
        if path.is_absolute() {
            Some(String::from("Path must be relative"))
        } else {
            None
        }
    }
}

/// CheckPath marker struct for absolute paths.
pub struct AbsolutePath {}

/// CheckPath implementation that checks if paths are absolute.
impl CheckPath for AbsolutePath {
    /// Returns `None` if `path` is absolute, or an error message
    /// otherwise.
    fn check_path(path: &Path) -> Option<String> {
        if !path.is_absolute() {
            Some(String::from("Path must be absolute"))
        } else {
            None
        }
    }
}
