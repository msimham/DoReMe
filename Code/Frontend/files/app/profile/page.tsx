"use client";

import { useState, useEffect } from "react";
import { Plus } from "lucide-react";
import ProfileProjectCard from "@/components/ProfileProjectCard";
import { Project } from "@/lib/types";
import { getProjects, saveProjects, updateProject } from "@/lib/storage";

const MOCK_PROFILE = {
  name: "Your Name",
  handle: "@yourhandle",
  location: "San Francisco, CA",
  abilities: ["producer", "composer", "musician"],
  lookingFor: ["singer", "writer"],
};

export default function ProfilePage() {
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    const stored = getProjects();
    if (stored.length === 0) {
      // Initialize with sample projects
      const initial: Project[] = [
        {
          id: "p1",
          title: "Project 1",
          isPublic: true,
          stage: "Demo",
          updatedAt: Date.now(),
        },
        {
          id: "p2",
          title: "Project 2",
          isPublic: true,
          stage: "Idea",
          updatedAt: Date.now(),
        },
        {
          id: "p3",
          title: "Private Draft 1",
          isPublic: false,
          stage: "Draft",
          updatedAt: Date.now(),
        },
      ];
      saveProjects(initial);
      setProjects(initial);
    } else {
      setProjects(stored);
    }
  }, []);

  const handleUpdateProject = (projectId: string, updates: Partial<Project>) => {
    updateProject(projectId, updates);
    setProjects((prev) =>
      prev.map((p) =>
        p.id === projectId ? { ...p, ...updates, updatedAt: Date.now() } : p
      )
    );
  };

  const handleAddProject = (isPublic: boolean) => {
    const newProject: Project = {
      id: `p${Date.now()}`,
      title: `Project ${projects.filter((p) => p.isPublic === isPublic).length + 1}`,
      isPublic,
      stage: "Idea",
      updatedAt: Date.now(),
    };

    const updated = [...projects, newProject];
    setProjects(updated);
    saveProjects(updated);
  };

  const publicProjects = projects.filter((p) => p.isPublic);
  const privateProjects = projects.filter((p) => !p.isPublic);

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        {/* Profile Header */}
        <div className="card p-8 mb-8">
          <div className="flex items-start gap-6">
            <div className="w-24 h-24 bg-black/5 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-3xl font-medium">{MOCK_PROFILE.name[0]}</span>
            </div>
            <div className="flex-1">
              <h1 className="text-3xl font-bold mb-2">{MOCK_PROFILE.name}</h1>
              <p className="text-black/50 mb-3">{MOCK_PROFILE.handle}</p>
              <p className="text-black/60 mb-4">{MOCK_PROFILE.location}</p>

              {/* Abilities */}
              <div className="mb-4">
                <h3 className="text-xs font-semibold text-black/60 mb-2 uppercase tracking-wide">
                  Abilities
                </h3>
                <div className="flex flex-wrap gap-2">
                  {MOCK_PROFILE.abilities.map((ability) => (
                    <span key={ability} className="chip">
                      {ability}
                    </span>
                  ))}
                </div>
              </div>

              {/* Looking for */}
              <div>
                <h3 className="text-xs font-semibold text-black/60 mb-2 uppercase tracking-wide">
                  Looking for
                </h3>
                <div className="flex flex-wrap gap-2">
                  {MOCK_PROFILE.lookingFor.map((role) => (
                    <span key={role} className="chip bg-black text-white border-black">
                      {role}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Public Projects */}
        <div className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Public Projects</h2>
            <button
              onClick={() => handleAddProject(true)}
              className="btn-primary flex items-center gap-2"
            >
              <Plus size={18} />
              Add Project
            </button>
          </div>

          {publicProjects.length === 0 ? (
            <div className="card p-12 text-center text-black/40">
              <p>No public projects yet</p>
              <p className="text-sm mt-1">Add your first project to showcase your work</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {publicProjects.map((project) => (
                <ProfileProjectCard
                  key={project.id}
                  project={project}
                  onUpdate={(updates) => handleUpdateProject(project.id, updates)}
                />
              ))}
            </div>
          )}
        </div>

        {/* Private Drafts */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold">Private Drafts</h2>
              <p className="text-sm text-black/50 mt-1">Only you can see these</p>
            </div>
            <button
              onClick={() => handleAddProject(false)}
              className="btn-secondary flex items-center gap-2"
            >
              <Plus size={18} />
              Add Draft
            </button>
          </div>

          {privateProjects.length === 0 ? (
            <div className="card p-12 text-center text-black/40">
              <p>No private drafts yet</p>
              <p className="text-sm mt-1">Create drafts to work on ideas privately</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {privateProjects.map((project) => (
                <ProfileProjectCard
                  key={project.id}
                  project={project}
                  onUpdate={(updates) => handleUpdateProject(project.id, updates)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
