package com.example.backendapp.service;

import com.example.backendapp.model.Pet;
import com.example.backendapp.repository.PetRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Service
public class PetService {

    private final PetRepository petRepository;

    @Autowired
    public PetService(PetRepository petRepository) {
        this.petRepository = petRepository;
    }

    // Create a new pet
    public Pet savePet(Pet pet) {
        if (!pet.isValid()) {
            throw new IllegalArgumentException("Pet data is invalid. Name, type, and birth date are required.");
        }
        
        // Additional validation for owner email if present
        if (pet.getOwnerEmail() != null && !pet.getOwnerEmail().isEmpty() && !isValidEmail(pet.getOwnerEmail())) {
            throw new IllegalArgumentException("Invalid owner email format");
        }
        
        return petRepository.save(pet);
    }

    // Retrieve a pet by ID
    public Optional<Pet> getPetById(Long id) {
        if (id == null || id <= 0) {
            throw new IllegalArgumentException("Invalid pet ID");
        }
        return petRepository.findById(id);
    }

    // Update an existing pet
    public Pet updatePet(Long id, Pet petDetails) {
        if (id == null || id <= 0) {
            throw new IllegalArgumentException("Invalid pet ID");
        }
        
        if (!petDetails.isValid()) {
            throw new IllegalArgumentException("Pet data is invalid. Name, type, and birth date are required.");
        }
        
        Optional<Pet> existingPet = petRepository.findById(id);
        if (existingPet.isPresent()) {
            Pet pet = existingPet.get();
            pet.setName(petDetails.getName());
            pet.setType(petDetails.getType());
            pet.setBreed(petDetails.getBreed());
            pet.setBirthDate(petDetails.getBirthDate());
            pet.setOwnerName(petDetails.getOwnerName());
            pet.setOwnerEmail(petDetails.getOwnerEmail());
            return petRepository.save(pet);
        } else {
            throw new RuntimeException("Pet not found with id: " + id);
        }
    }

    // Delete a pet
    public void deletePet(Long id) {
        if (id == null || id <= 0) {
            throw new IllegalArgumentException("Invalid pet ID");
        }
        
        Optional<Pet> pet = petRepository.findById(id);
        if (pet.isPresent()) {
            petRepository.deleteById(id);
        } else {
            throw new RuntimeException("Pet not found with id: " + id);
        }
    }

    // Get all pets
    public List<Pet> getAllPets() {
        return petRepository.findAll();
    }

    // Find pets by type
    public List<Pet> findPetsByType(String type) {
        if (type == null || type.trim().isEmpty()) {
            throw new IllegalArgumentException("Pet type cannot be empty");
        }
        return petRepository.findByType(type);
    }

    // Find pets by owner name
    public List<Pet> findPetsByOwnerName(String ownerName) {
        if (ownerName == null || ownerName.trim().isEmpty()) {
            throw new IllegalArgumentException("Owner name cannot be empty");
        }
        return petRepository.findByOwnerName(ownerName);
    }

    // Find pets by breed
    public List<Pet> findPetsByBreed(String breed) {
        if (breed == null || breed.trim().isEmpty()) {
            throw new IllegalArgumentException("Breed cannot be empty");
        }
        return petRepository.findByBreed(breed);
    }

    // Find pets born after a specific date
    public List<Pet> findPetsBornAfter(LocalDate date) {
        if (date == null) {
            throw new IllegalArgumentException("Date cannot be null");
        }
        return petRepository.findByBirthDateAfter(date);
    }

    // Find pets by type and breed
    public List<Pet> findPetsByTypeAndBreed(String type, String breed) {
        if (type == null || type.trim().isEmpty()) {
            throw new IllegalArgumentException("Pet type cannot be empty");
        }
        if (breed == null || breed.trim().isEmpty()) {
            throw new IllegalArgumentException("Breed cannot be empty");
        }
        return petRepository.findPetsByTypeAndBreed(type, breed);
    }

    // Search pets by name containing a string
    public List<Pet> searchPetsByName(String nameFragment) {
        if (nameFragment == null || nameFragment.trim().isEmpty()) {
            throw new IllegalArgumentException("Name search term cannot be empty");
        }
        return petRepository.findPetsWithNameContaining(nameFragment);
    }

    // Helper method to validate email format
    private boolean isValidEmail(String email) {
        String emailRegex = "^[A-Za-z0-9+_.-]+@(.+)$";
        return email.matches(emailRegex);
    }
}