#!/usr/bin/python

# Copyright The OpenTelemetry Authors
# SPDX-License-Identifier: Apache-2.0

import random
import requests
import time
from locust import FastHttpUser, task, constant

class PetClinicUser(FastHttpUser):

    # Make each user wait 5 seconds after it executed its task
    # before picking up another one
    wait_time = constant(5)

    def wait_for_services(self):
        # Check health endpoints of each service
        for service, port in [('customers', 8081), ('visits', 8082), ('vets', 8083)]:
            url = f"http://{service}-service:{port}/actuator/health"
            try:
                response = self.client.get(url)
                response.raise_for_status()
            except requests.exceptions.RequestException:
                print(f"Waiting for {service} service to become healthy...")
                time.sleep(5)
                self.wait_for_services()
                return

    # viewOwner task is 2x more likely to be picked up by a user than editPetType
    @task(2)
    def viewOwner(self):
        self.client.get("/")
        self.client.get("/api/customer/owners")
        owner_id = random.randint(1, 10)
        self.client.get(f"/api/gateway/owners/{owner_id}", name="/api/gateway/owners/{ownerId}")
        self.client.get("/api/vet/vets")

    @task(1)
    def editPetType(self):
        self.client.get("/")
        self.client.get("/api/customer/owners")
        owner_id = random.randint(1, 10)
        self.client.get(f"/api/gateway/owners/{owner_id}", name="/api/gateway/owners/{ownerId}")
        pet_id = random.randint(1, 13)
        petResponse = self.client.get(f"/api/customer/owners/{owner_id}/pets/{ pet_id }", name="/api/customer/owners/{ownerId}/pets/{petId}")
        petName = petResponse.json()["name"]
        petBirthDate = petResponse.json()["birthDate"]
        petTypeResponse = self.client.get("/api/customer/petTypes")
        petTypes = petTypeResponse.json()
        random_pet_type_id = random.choice(petTypes)["id"]
        self.client.put(
            f"/api/customer/owners/{ owner_id }/pets/{ pet_id }",
            json={"birthDate": petBirthDate, "id": pet_id, "name": petName, "typeId": random_pet_type_id},
            name="api/customer/owners/{ownerId}/pets/{petId}"
        )
        self.client.get("/api/customer/owners")

    @task(1)
    def createRandomPet(self):
        pet_id = random.randint(1,5)
        self.client.post(
            f"/api/customer/owners/2/pets",
            json={"id": 0, "name": "Thorsten", "birthDate": "2001-09-0314:00:00.000Z", "typeId": pet_id},
            name="Create Random Pet /api/customer/owners/2/pets"
        )

    @task(1)
    def createSlowPet(self):
        self.client.post(
            f"/api/customer/owners/1/pets",
            json={"id": 0, "name": "Johnny", "birthDate": "2000-05-25T22:00:00.000Z", "typeId": "6"},
            name="Create Slow Pet (Hamster) /api/customer/owners/1/pets"
        )

    @task(1)
    def createExceptionPet(self):
        self.client.post(
            f"/api/customer/owners/1/pets",
            json={"id": 0, "name": "Tassilo", "birthDate": "2000-05-25T22:00:00.000Z", "typeId": "5"},
            name="Create Exception Pet (Bird) /api/customer/owners/1/pets"
        )






