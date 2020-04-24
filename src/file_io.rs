use encoding::label::encoding_from_whatwg_label;
use encoding::{decode, DecoderTrap};
use std::fs::File;
use std::io::{BufReader, Error, ErrorKind, Read, Result, Seek, SeekFrom};
use std::path::Path;

/// Read the full contents of a file as a string.
///
/// This decodes the contents of the file using the specified encoding.
pub fn read_file(path: &Path, encoding: &str) -> Result<String> {
    let encoding = encoding_from_whatwg_label(encoding).ok_or(Error::new(
        ErrorKind::InvalidInput,
        format!("Invalid or unsupported encoding: {}", encoding),
    ))?;

    let f = File::open(path)?;
    let mut handle = BufReader::new(f);

    let mut buffer = Vec::new();
    handle.seek(SeekFrom::Start(0))?;
    handle.read_to_end(&mut buffer)?;
    decode(buffer.as_slice(), DecoderTrap::Strict, encoding)
        .0
        .map_err(|e| Error::new(ErrorKind::InvalidData, e.to_owned().to_string()))
}
