import { initClassroomAssignment } from "./modules/classroom-assignment.js";

const featureInitializers = [initClassroomAssignment];

for (const initializeFeature of featureInitializers) {
  try {
    initializeFeature(document);
  } catch (error) {
    console.error("Hidden project feature failed to initialize.", error);
  }
}
