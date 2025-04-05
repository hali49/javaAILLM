package com.example.backendapp.controller;

import com.example.backendapp.model.Pet;
import com.example.backendapp.service.PetService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/pets")
public class PetController {

    private final PetService petService;

    @Autowired
    public PetController(PetService petService) {
        this.petService = petService;
    }

    // Create a new pet
    @PostMapping
    public ResponseEntity<Pet> createPet(@RequestBody Pet pet) {
        try {
            Pet savedPet = petService.savePet(pet);
            return new ResponseEntity<>(savedPet, HttpStatus.CREATED);
        } catch (IllegalArgumentException e) {
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
    }

    // Get all pets
    @GetMapping
    public ResponseEntity<List<Pet>> getAllPets() {
        List<Pet> pets = petService.getAllPets();
        return new ResponseEntity<>(pets, HttpStatus.OK);
    }

    // Get a pet by ID
    @GetMapping("/{id}")
    public ResponseEntity<Pet> getPetById(@PathVariable Long id) {
        try {
            Optional<Pet> pet = petService.getPetById(id);
            return pet.map(value -> new ResponseEntity<>(value, HttpStatus.OK))
                    .orElseGet(() -> new ResponseEntity<>(HttpStatus.NOT_FOUND));
        } catch (IllegalArgumentException e) {
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
    }

    // Update a pet
    @PutMapping("/{id}")
    public ResponseEntity<Pet> updatePet(@PathVariable Long id, @RequestBody Pet petDetails) {
        try {
            Pet updatedPet = petService.updatePet(id, petDetails);
            return new ResponseEntity<>(updatedPet, HttpStatus.OK);
        } catch (RuntimeException e) {
            if (e instanceof IllegalArgumentException) {
                return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
            }
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
    }

    // Delete a pet
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deletePet(@PathVariable Long id) {
        try {
            petService.deletePet(id);
            return new ResponseEntity<>(HttpStatus.NO_CONTENT);
        } catch (RuntimeException e) {
            if (e instanceof IllegalArgumentException) {
                return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
            }
            return new ResponseEntity<>(HttpStatus.NOT_FOUND);
        }
    }

    // Find pets by type
    @GetMapping("/type/{type}")
    public ResponseEntity<List<Pet>> getPetsByType(@PathVariable String type) {
        try {
            List<Pet> pets = petService.findPetsByType(type);
            return new ResponseEntity<>(pets, HttpStatus.OK);
        } catch (IllegalArgumentException e) {
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
    }

    // Find pets by owner name
    @GetMapping("/owner/{ownerName}")
    public ResponseEntity<List<Pet>> getPetsByOwnerName(@PathVariable String ownerName) {
        try {
            List<Pet> pets = petService.findPetsByOwnerName(ownerName);
            return new ResponseEntity<>(pets, HttpStatus.OK);
        } catch (IllegalArgumentException e) {
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
    }

    // Find pets by breed
    @GetMapping("/breed/{breed}")
    public ResponseEntity<List<Pet>> getPetsByBreed(@PathVariable String breed) {
        try {
            List<Pet> pets = petService.findPetsByBreed(breed);
            return new ResponseEntity<>(pets, HttpStatus.OK);
        } catch (IllegalArgumentException e) {
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
    }

    // Find pets born after a specific date
    @GetMapping("/born-after")
    public ResponseEntity<List<Pet>> getPetsBornAfter(@RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        try {
            List<Pet> pets = petService.findPetsBornAfter(date);
            return new ResponseEntity<>(pets, HttpStatus.OK);
        } catch (IllegalArgumentException e) {
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
    }

    // Find pets by type and breed
    @GetMapping("/search")
    public ResponseEntity<List<Pet>> getPetsByTypeAndBreed(
            @RequestParam String type,
            @RequestParam String breed) {
        try {
            List<Pet> pets = petService.findPetsByTypeAndBreed(type, breed);
            return new ResponseEntity<>(pets, HttpStatus.OK);
        } catch (IllegalArgumentException e) {
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
    }

    // Search pets by name
    @GetMapping("/search/name")
    public ResponseEntity<List<Pet>> searchPetsByName(@RequestParam String name) {
        try {
            List<Pet> pets = petService.searchPetsByName(name);
            return new ResponseEntity<>(pets, HttpStatus.OK);
        } catch (IllegalArgumentException e) {
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }
    }
}