use std::path::Path;

pub trait CheckPath {
    fn check_path(path: &Path) -> Option<String>;
}

pub struct RelativePath {}

impl CheckPath for RelativePath {
    fn check_path(path: &Path) -> Option<String> {
        if path.is_absolute() {
            Some(String::from("Path must be relative"))
        } else {
            None
        }
    }
}

pub struct AbsolutePath {}

impl CheckPath for AbsolutePath {
    fn check_path(path: &Path) -> Option<String> {
        if !path.is_absolute() {
            Some(String::from("Path must be absolute"))
        } else {
            None
        }
    }
}
