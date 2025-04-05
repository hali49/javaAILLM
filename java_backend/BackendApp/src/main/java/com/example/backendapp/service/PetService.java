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

    public Pet savePet(Pet pet) {
        if (pet == null) throw new IllegalArgumentException("Pet cannot be null");
        return petRepository.save(pet);
    }

    public List<Pet> getAllPets() {
        return petRepository.findAll();
    }

    public Optional<Pet> getPetById(Long id) {
        return petRepository.findById(id);
    }

    public Pet updatePet(Long id, Pet petDetails) {
        Pet pet = petRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Pet not found"));
        pet.setName(petDetails.getName());
        pet.setType(petDetails.getType());
        pet.setBreed(petDetails.getBreed());
        pet.setBirthDate(petDetails.getBirthDate());
        pet.setOwnerName(petDetails.getOwnerName());
        pet.setOwnerEmail(petDetails.getOwnerEmail());
        return petRepository.save(pet);
    }

    public void deletePet(Long id) {
        if (!petRepository.existsById(id)) {
            throw new RuntimeException("Pet not found");
        }
        petRepository.deleteById(id);
    }

    public List<Pet> findPetsByType(String type) {
        return petRepository.findByType(type);
    }

    public List<Pet> findPetsByOwnerName(String ownerName) {
        return petRepository.findByOwnerName(ownerName);
    }

    public List<Pet> findPetsByBreed(String breed) {
        return petRepository.findByBreed(breed);
    }

    public List<Pet> findPetsBornAfter(LocalDate date) {
        return petRepository.findByBirthDateAfter(date);
    }

    public List<Pet> findPetsByTypeAndBreed(String type, String breed) {
        return petRepository.findByTypeAndBreed(type, breed);
    }

    public List<Pet> searchPetsByName(String name) {
        return petRepository.findByNameContainingIgnoreCase(name);
    }
}
