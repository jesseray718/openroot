#include <iostream>
#include <chrono>
#include <iomanip>
#include <openroot/thermo.hpp>

int main() {
    using namespace openroot::thermo;

    // Initialize source node with ample energy/mass capacity
    StateNode src{1, 50'000'000'000LL, 20'000'000ULL, 0};
    StateNode dst{2, 0LL, 0ULL, 0};

    // Quantum transfer per tick
    FluxQuantum flux{1'000LL, 1ULL, LANDAUER_MINIMUM_PER_BIT_OP};

    constexpr std::size_t ITERATIONS = 10'000'000;

    std::cout << "Starting 0D state transition benchmark (" << ITERATIONS << " ops)...\n";

    auto start = std::chrono::high_resolution_clock::now();

    std::size_t success_count = 0;
    for (std::size_t i = 0; i < ITERATIONS; ++i) {
        auto status = execute_0d_transition(src, dst, flux);
        if (status == TransitionStatus::Success) {
            ++success_count;
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> duration = end - start;

    double seconds = duration.count() / 1000.0;
    double million_ops_per_sec = (ITERATIONS / seconds) / 1'000'000.0;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "========================================================\n";
    std::cout << "OPENROOT 0D THERMODYNAMIC ENGINE BENCHMARK\n";
    std::cout << "========================================================\n";
    std::cout << "Iterations:          " << ITERATIONS << "\n";
    std::cout << "Successful:          " << success_count << "\n";
    std::cout << "Total Time:          " << duration.count() << " ms\n";
    std::cout << "Throughput:          " << million_ops_per_sec << " Million transitions/sec\n";
    std::cout << "Final Src Energy:    " << src.energy << " nJ\n";
    std::cout << "Final Dst Energy:    " << dst.energy << " nJ\n";
    std::cout << "Accumulated Entropy: " << dst.entropy << " micro-kB\n";
    std::cout << "========================================================\n";

    return 0;
}
