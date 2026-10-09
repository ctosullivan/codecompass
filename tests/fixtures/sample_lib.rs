/// Adds two numbers together.
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

pub struct Point {
    pub x: i32,
    pub y: i32,
}

fn internal_helper() -> bool {
    true
}

/// A function whose signature spans multiple lines — the adapter's
/// coarse line-based scan only captures the opening line.
pub fn multi_line_signature(
    a: i32,
    b: i32,
) -> i32 {
    a + b
}
