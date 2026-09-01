// Explicit translation unit for the header-only thermodynamic kernel.
//
// include/openroot/thermo.hpp only contains declarations, inline functions
// and a function template. Compiling the header directly (as a .hpp file)
// causes g++ to treat it as a precompiled header input, producing a GCH
// file instead of object code -- which yields an invalid ELF binary when
// used as a shared library. This wrapper includes the header as a normal
// translation unit and explicitly instantiates the template so the
// compiler emits real machine code for it into libthermo.so.

#include "openroot/thermo.hpp"

namespace openroot::thermo {

template TransitionStatus execute_0d_transition<StateNode>(
    StateNode& source,
    StateNode& destination,
    const FluxQuantum& flux) noexcept;

} // namespace openroot::thermo

// openroot_execute_0d_transition() is declared `inline` in the header, so it
// is only emitted into the object file if it is actually referenced from a
// translation unit. Taking its address here forces the compiler to generate
// (non-inlined) code for the extern "C" symbol so it is present and
// exported in libthermo.so for Python's ctypes to load.
extern "C" {
decltype(&openroot_execute_0d_transition) openroot_execute_0d_transition_force_link =
    &openroot_execute_0d_transition;
}

