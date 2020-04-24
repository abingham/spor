pub mod steps;
pub mod world;
use cucumber_rust::{before, after, cucumber};

// Declares a before handler function named `a_before_fn`
before!(a_before_fn => |_scenario| {

});

// Declares an after handler function named `an_after_fn`
after!(an_after_fn => |_scenario| {

});

// A setup function to be called before everything else
fn setup() {}

cucumber! {
    features: "./tests/e2e/features", // Path to our feature files
    world: world::World, // The world needs to be the same for steps and the main cucumber call
    steps: &[
        steps::cli::steps // the `steps!` macro creates a `steps` function in a module
    ],
    setup: setup, // Optional; called once before everything
    before: &[
        a_before_fn // Optional; called before each scenario
    ],
    after: &[
        an_after_fn // Optional; called after each scenario
    ]
}

// import subprocess

// from radish import given, when, then
