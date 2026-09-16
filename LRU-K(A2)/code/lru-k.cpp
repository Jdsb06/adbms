#include <algorithm>
#include <climits>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace std;

using PageId = long long;

struct History {
    // HIST[1..K] contains timestamps of the K most recent uncorrelated references.
    vector<long long> HIST;

    // Most recent physical reference, correlated or not.
    long long LAST = 0;

    bool inBuffer = false;
    bool exists = false;
};

class LRUKCache {
public:
    int K;
    size_t bufferSize;
    long long correlatedRefPeriod;
    long long retainedInfoPeriod;
    bool verbose;

    vector<History> histories;
    vector<PageId> bufferPool;

    long long hits = 0;
    long long misses = 0;

    LRUKCache(int k = 2,
              size_t bSize = 60,
              long long crp = 0,
              long long rip = LLONG_MAX / 4,
              bool verb = false)
        : K(k),
          bufferSize(bSize),
          correlatedRefPeriod(crp),
          retainedInfoPeriod(rip),
          verbose(verb) {
        histories.resize(10200);
    }

    void reset() {
        fill(histories.begin(), histories.end(), History{});
        bufferPool.clear();
        hits = 0;
        misses = 0;
    }

    void ensureCapacity(PageId page) {
        if (static_cast<size_t>(page) >= histories.size()) {
            histories.resize(page + 10000);
        }
    }

    bool isResident(PageId page) const {
        if (static_cast<size_t>(page) >= histories.size()) return false;
        return histories[page].inBuffer;
    }

    void purgeOldHistory(long long currentTime) {
        if (retainedInfoPeriod >= LLONG_MAX / 4) return;
        for (size_t p = 0; p < histories.size(); ++p) {
            auto &history = histories[p];
            if (history.exists && !history.inBuffer &&
                currentTime - history.LAST > retainedInfoPeriod) {
                if (verbose) {
                    cout << "      [purge] HIST(" << p << ") discarded\n";
                }
                history.exists = false;
                history.HIST.clear();
            }
        }
    }

    void printBuffer() const {
        if (!verbose) return;
        cout << "      Buffer = { ";
        for (PageId page : bufferPool) {
            cout << page << ' ';
        }
        cout << "}\n";
    }

    bool referencePage(PageId page, long long currentTime) {
        ensureCapacity(page);
        History &history = histories[page];
        const bool hit = history.inBuffer;

        if (verbose) {
            cout << "t=" << setw(6) << currentTime
                 << " ref=" << setw(8) << page;
        }

        if (hit) {
            if (currentTime - history.LAST > correlatedRefPeriod) {
                const long long correlatedPeriodLength = history.LAST - history.HIST[1];

                for (int i = K; i >= 2; --i) {
                    if (history.HIST[i - 1] == 0) {
                        history.HIST[i] = 0;
                    } else {
                        history.HIST[i] = history.HIST[i - 1] + correlatedPeriodLength;
                    }
                }

                history.HIST[1] = currentTime;

                if (verbose) {
                    cout << " [HIT, uncorrelated]\n";
                }
            } else {
                if (verbose) {
                    cout << " [HIT, correlated]\n";
                }
            }

            history.LAST = currentTime;
            ++hits;
        } else {
            if (verbose) {
                cout << " [MISS]\n";
            }
            ++misses;

            if (bufferPool.size() >= bufferSize) {
                PageId victim = -1;
                bool foundEligibleVictim = false;

                long long smallestHistoryTimestamp = LLONG_MAX;

                for (PageId candidate : bufferPool) {
                    const History &candidateHistory = histories[candidate];
                    const bool eligible = (currentTime - candidateHistory.LAST > correlatedRefPeriod);

                    if (!eligible) {
                        continue;
                    }

                    const long long historyKey = candidateHistory.HIST[K];

                    if (!foundEligibleVictim || historyKey < smallestHistoryTimestamp) {
                        victim = candidate;
                        smallestHistoryTimestamp = historyKey;
                        foundEligibleVictim = true;
                    } else if (historyKey == smallestHistoryTimestamp &&
                               candidateHistory.LAST < histories[victim].LAST) {
                        victim = candidate;
                    }
                }

                if (!foundEligibleVictim) {
                    victim = bufferPool.front();
                    for (PageId candidate : bufferPool) {
                        if (histories[candidate].LAST < histories[victim].LAST) {
                            victim = candidate;
                        }
                    }
                    if (verbose) {
                        cout << "      No page outside CRP; emergency LRU victim = " << victim << "\n";
                    }
                } else if (verbose) {
                    cout << "      LRU-" << K << " victim = " << victim
                         << ", HIST(" << K << ") = " << smallestHistoryTimestamp << "\n";
                }

                auto victimPosition = find(bufferPool.begin(), bufferPool.end(), victim);
                if (victimPosition == bufferPool.end()) {
                    throw logic_error("Selected victim is not resident");
                }

                bufferPool.erase(victimPosition);
                histories[victim].inBuffer = false;
            } else if (verbose) {
                cout << "      Free buffer frame used\n";
            }

            bufferPool.push_back(page);

            if (!history.exists) {
                history.exists = true;
                history.HIST.assign(K + 1, 0);
                history.HIST[1] = currentTime;
                history.LAST = currentTime;
                history.inBuffer = true;
            } else {
                for (int i = K; i >= 2; --i) {
                    history.HIST[i] = history.HIST[i - 1];
                }
                history.HIST[1] = currentTime;
                history.LAST = currentTime;
                history.inBuffer = true;
            }
        }

        purgeOldHistory(currentTime);
        printBuffer();

        return hit;
    }

    double getHitRatio() const {
        long long total = hits + misses;
        if (total == 0) return 0.0;
        return static_cast<double>(hits) / static_cast<double>(total);
    }
};

vector<PageId> generateTwoPoolWorkload(size_t numRequests = 100000, uint32_t seed = 42) {
    mt19937 rng(seed);
    uniform_int_distribution<PageId> distPool1(1, 100);
    uniform_int_distribution<PageId> distPool2(101, 10100);

    vector<PageId> trace;
    trace.reserve(numRequests);

    for (size_t i = 0; i < numRequests; ++i) {
        if (i % 2 == 0) {
            trace.push_back(distPool1(rng));
        } else {
            trace.push_back(distPool2(rng));
        }
    }
    return trace;
}

void runTwoPoolSimulation(size_t numRequests = 100000) {
    vector<size_t> bufferSizes = {60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 350, 400, 450};

    cout << "===============================================================\n";
    cout << "           LRU-K TWO-POOL EXPERIMENT SIMULATION                \n";
    cout << "===============================================================\n";
    cout << "Workload Parameters:\n";
    cout << "  - Pool N1 (Index): 100 pages (IDs 1 to 100)\n";
    cout << "  - Pool N2 (Data) : 10,000 pages (IDs 101 to 10100)\n";
    cout << "  - Alternating access pattern: N1, N2, N1, N2...\n";
    cout << "  - Total References: " << numRequests << "\n";
    cout << "  - CRP = 0, RIP = LLONG_MAX / 4\n";
    cout << "===============================================================\n\n";

    vector<PageId> trace = generateTwoPoolWorkload(numRequests, 42);

    cout << "+--------+---------+---------+---------+\n";
    cout << "|   B    |  LRU-1  |  LRU-2  |  LRU-3  |\n";
    cout << "+--------+---------+---------+---------+\n";

    for (size_t B : bufferSizes) {
        LRUKCache lru1(1, B, 0, LLONG_MAX / 4, false);
        LRUKCache lru2(2, B, 0, LLONG_MAX / 4, false);
        LRUKCache lru3(3, B, 0, LLONG_MAX / 4, false);

        long long currentTime = 0;
        for (PageId page : trace) {
            ++currentTime;
            lru1.referencePage(page, currentTime);
            lru2.referencePage(page, currentTime);
            lru3.referencePage(page, currentTime);
        }

        cout << "| " << setw(6) << B << " | "
             << fixed << setprecision(3)
             << setw(7) << lru1.getHitRatio() << " | "
             << setw(7) << lru2.getHitRatio() << " | "
             << setw(7) << lru3.getHitRatio() << " |\n";
    }
    cout << "+--------+---------+---------+---------+\n";
}

void runConvergenceSimulation(size_t bufferSize = 100, size_t numRequests = 100000, size_t step = 1000) {
    vector<PageId> trace = generateTwoPoolWorkload(numRequests, 42);
    LRUKCache lru1(1, bufferSize);
    LRUKCache lru2(2, bufferSize);
    LRUKCache lru3(3, bufferSize);

    cout << "t,LRU1,LRU2,LRU3\n";
    long long currentTime = 0;
    for (PageId page : trace) {
        ++currentTime;
        lru1.referencePage(page, currentTime);
        lru2.referencePage(page, currentTime);
        lru3.referencePage(page, currentTime);

        if (currentTime % step == 0 || currentTime == (long long)numRequests) {
            cout << currentTime << ","
                 << fixed << setprecision(5)
                 << lru1.getHitRatio() << ","
                 << lru2.getHitRatio() << ","
                 << lru3.getHitRatio() << "\n";
        }
    }
}

void runKSensitivitySimulation(size_t numRequests = 100000) {
    vector<size_t> bufferSizes = {60, 100, 140, 200};
    vector<int> kValues = {1, 2, 3, 4, 5};
    vector<PageId> trace = generateTwoPoolWorkload(numRequests, 42);

    cout << "B,K,HitRatio\n";
    for (size_t B : bufferSizes) {
        for (int K : kValues) {
            LRUKCache lru(K, B);
            long long currentTime = 0;
            for (PageId page : trace) {
                ++currentTime;
                lru.referencePage(page, currentTime);
            }
            cout << B << "," << K << "," << fixed << setprecision(5) << lru.getHitRatio() << "\n";
        }
    }
}

int main(int argc, char *argv[]) {
    try {
        if (argc > 1 && string(argv[1]) == "--convergence") {
            size_t b = (argc > 2) ? stoull(argv[2]) : 100;
            size_t n = (argc > 3) ? stoull(argv[3]) : 100000;
            runConvergenceSimulation(b, n, 1000);
            return 0;
        }

        if (argc > 1 && string(argv[1]) == "--k-sensitivity") {
            size_t n = (argc > 2) ? stoull(argv[2]) : 100000;
            runKSensitivitySimulation(n);
            return 0;
        }

        size_t numRequests = 100000;
        if (argc > 1) {
            numRequests = stoull(argv[1]);
        }

        runTwoPoolSimulation(numRequests);
        return 0;
    } catch (const exception &error) {
        cerr << "Error: " << error.what() << '\n';
        return 1;
    }
}
