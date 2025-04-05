package com.example.backendapp.repository;

import com.example.backendapp.model.Pet;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface PetRepository extends JpaRepository<Pet, Long> {
    List<Pet> findByType(String type);
    List<Pet> findByOwnerName(String ownerName);
    List<Pet> findByBreed(String breed);
    List<Pet> findByBirthDateAfter(LocalDate date);
    List<Pet> findByTypeAndBreed(String type, String breed);
    List<Pet> findByNameContainingIgnoreCase(String name);
}
