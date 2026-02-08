"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Filter } from "lucide-react";
import MatchCard from "@/components/MatchCard";
import { Musician, Ability, MatchState } from "@/lib/types";
import { mockMusicians } from "@/lib/mockData";
import { getMatchState, updateMatchState } from "@/lib/storage";

export default function FindPage() {
  const router = useRouter();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [matchState, setMatchState] = useState<MatchState>({});
  const [showFilters, setShowFilters] = useState(false);
  const [abilityFilter, setAbilityFilter] = useState<Ability[]>([]);
  const [lookingForFilter, setLookingForFilter] = useState<Ability | null>(null);
  const [locationFilter, setLocationFilter] = useState("");

  useEffect(() => {
    const state = getMatchState();
    setMatchState(state);

    // Keyboard shortcuts
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft") handlePass();
      if (e.key === "ArrowRight") handleLike();
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [currentIndex]);

  const availableMusicians = mockMusicians.filter((m) => {
    if (matchState[m.id]) return false;

    if (abilityFilter.length > 0) {
      const hasAbility = abilityFilter.some((a) => m.abilities.includes(a));
      if (!hasAbility) return false;
    }

    if (lookingForFilter) {
      if (!m.lookingFor.includes(lookingForFilter)) return false;
    }

    if (locationFilter) {
      if (!m.location.toLowerCase().includes(locationFilter.toLowerCase())) {
        return false;
      }
    }

    return true;
  });

  const currentMusician = availableMusicians[currentIndex];

  const handleLike = () => {
    if (!currentMusician) return;

    updateMatchState(currentMusician.id, "liked");
    setMatchState((prev) => ({ ...prev, [currentMusician.id]: "liked" }));

    // Show match modal
    setTimeout(() => {
      if (
        confirm(
          `It's a match with ${currentMusician.name}! Send them a message?`
        )
      ) {
        router.push("/dm");
      }
    }, 300);

    nextMusician();
  };

  const handlePass = () => {
    if (!currentMusician) return;

    updateMatchState(currentMusician.id, "passed");
    setMatchState((prev) => ({ ...prev, [currentMusician.id]: "passed" }));

    nextMusician();
  };

  const nextMusician = () => {
    if (currentIndex < availableMusicians.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const toggleAbilityFilter = (ability: Ability) => {
    setAbilityFilter((prev) =>
      prev.includes(ability)
        ? prev.filter((a) => a !== ability)
        : [...prev, ability]
    );
    setCurrentIndex(0);
  };

  const allAbilities: Ability[] = ["writer", "producer", "composer", "musician", "singer"];

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold">Find Musicians</h1>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn-secondary flex items-center gap-2"
          >
            <Filter size={18} />
            Filters
          </button>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="card p-6 mb-8 animate-fade-in">
            <div className="space-y-6">
              {/* Ability filter */}
              <div>
                <label className="block text-sm font-semibold mb-3">
                  Filter by Ability
                </label>
                <div className="flex flex-wrap gap-2">
                  {allAbilities.map((ability) => (
                    <button
                      key={ability}
                      onClick={() => toggleAbilityFilter(ability)}
                      className={`chip cursor-pointer transition-colors ${
                        abilityFilter.includes(ability)
                          ? "bg-black text-white border-black"
                          : "hover:bg-black/10"
                      }`}
                    >
                      {ability}
                    </button>
                  ))}
                </div>
              </div>

              {/* Looking for filter */}
              <div>
                <label className="block text-sm font-semibold mb-3">
                  Looking for
                </label>
                <div className="flex flex-wrap gap-2">
                  {allAbilities.map((ability) => (
                    <button
                      key={ability}
                      onClick={() =>
                        setLookingForFilter(
                          lookingForFilter === ability ? null : ability
                        )
                      }
                      className={`chip cursor-pointer transition-colors ${
                        lookingForFilter === ability
                          ? "bg-black text-white border-black"
                          : "hover:bg-black/10"
                      }`}
                    >
                      {ability}
                    </button>
                  ))}
                </div>
              </div>

              {/* Location filter */}
              <div>
                <label className="block text-sm font-semibold mb-3">
                  Location
                </label>
                <input
                  type="text"
                  value={locationFilter}
                  onChange={(e) => {
                    setLocationFilter(e.target.value);
                    setCurrentIndex(0);
                  }}
                  placeholder="Enter city or state..."
                  className="input"
                />
              </div>

              {/* Clear filters */}
              {(abilityFilter.length > 0 || lookingForFilter || locationFilter) && (
                <button
                  onClick={() => {
                    setAbilityFilter([]);
                    setLookingForFilter(null);
                    setLocationFilter("");
                    setCurrentIndex(0);
                  }}
                  className="text-sm text-black/60 hover:text-black transition-colors"
                >
                  Clear all filters
                </button>
              )}
            </div>
          </div>
        )}

        {/* Cards */}
        <div className="flex items-center justify-center min-h-[600px]">
          {availableMusicians.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-black/40 text-lg mb-2">
                No more musicians to show
              </p>
              <p className="text-black/30 text-sm">
                Try adjusting your filters or check back later
              </p>
            </div>
          ) : currentMusician ? (
            <MatchCard
              key={currentMusician.id}
              musician={currentMusician}
              onLike={handleLike}
              onPass={handlePass}
            />
          ) : (
            <div className="text-center py-20">
              <p className="text-black/40 text-lg mb-2">
                You've seen all musicians!
              </p>
              <p className="text-black/30 text-sm">
                Check your matches in DMs
              </p>
            </div>
          )}
        </div>

        {/* Progress indicator */}
        {availableMusicians.length > 0 && (
          <div className="text-center mt-6 text-sm text-black/40">
            {currentIndex + 1} / {availableMusicians.length}
          </div>
        )}
      </div>
    </div>
  );
}
