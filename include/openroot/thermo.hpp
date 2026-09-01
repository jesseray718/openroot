#pragma once

#include <compare>
#include <concepts>
#include <cstdint>
#include <limits>
#include <type_traits>

namespace openroot::thermo {

using joules_t          = std::int64_t;
using mass_ug_t         = std::uint64_t;
using entropy_fixed_t   = std::uint64_t;
using node_id_t         = std::uint32_t;

enum class TransitionStatus : std::uint8_t {
    Success = 0,
    InsufficientEnergySource,
    InsufficientMassSource,
    LandauerBoundViolation,
    IntegerOverflowGuard,
    NonConservedEnergyState
};

template <typename T>
concept ZeroDimNode = requires(T node) {
    { node.id }      -> std::convertible_to<node_id_t>;
    { node.energy }  -> std::same_as<joules_t&>;
    { node.mass }    -> std::same_as<mass_ug_t&>;
    { node.entropy } -> std::same_as<entropy_fixed_t&>;
};

struct alignas(32) StateNode {
    node_id_t        id{0};
    joules_t         energy{0};   // nano-Joules
    mass_ug_t        mass{0};     // micro-grams
    entropy_fixed_t  entropy{0};  // micro-kB units

    constexpr auto operator<=>(const StateNode&) const = default;
};

struct FluxQuantum {
    joules_t        delta_energy{0};
    mass_ug_t       delta_mass{0};
    entropy_fixed_t generated_entropy{0}; // Enforces Second Law: dS >= 0
};

inline constexpr entropy_fixed_t LANDAUER_MINIMUM_PER_BIT_OP = 693ULL; // ~0.693 micro-kB

template <ZeroDimNode Node = StateNode>
[[nodiscard]] constexpr TransitionStatus execute_0d_transition(
    Node& source,
    Node& destination,
    const FluxQuantum& flux) noexcept 
{
    if (source.energy < flux.delta_energy) {
        return TransitionStatus::InsufficientEnergySource;
    }
    if (source.mass < flux.delta_mass) {
        return TransitionStatus::InsufficientMassSource;
    }
    if (flux.generated_entropy < LANDAUER_MINIMUM_PER_BIT_OP) {
        return TransitionStatus::LandauerBoundViolation;
    }
    if (destination.energy > std::numeric_limits<joules_t>::max() - flux.delta_energy ||
        destination.mass > std::numeric_limits<mass_ug_t>::max() - flux.delta_mass) {
        return TransitionStatus::IntegerOverflowGuard;
    }

    const joules_t initial_total_energy = source.energy + destination.energy;
    
    source.energy      -= flux.delta_energy;
    destination.energy += flux.delta_energy;

    source.mass        -= flux.delta_mass;
    destination.mass   += flux.delta_mass;

    destination.entropy += flux.generated_entropy;

    if ((source.energy + destination.energy) != initial_total_energy) {
        return TransitionStatus::NonConservedEnergyState;
    }

    return TransitionStatus::Success;
}

} // namespace openroot::thermo
