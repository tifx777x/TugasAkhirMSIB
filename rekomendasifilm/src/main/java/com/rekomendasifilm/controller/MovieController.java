package com.rekomendasifilm.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.client.RestTemplate;

@Controller
public class MovieController {
    private final String BACKEND_URL = "http://localhost:5000";

    @GetMapping("/")
    public String home(Model model) {
        RestTemplate restTemplate = new RestTemplate();
        String url = BACKEND_URL + "/recommend";
        Object movies = restTemplate.getForObject(url, Object.class);
        model.addAttribute("movies", movies);
        return "home";
    }

    @GetMapping("/search")
    public String search(@RequestParam String query, Model model) {
        RestTemplate restTemplate = new RestTemplate();
        String url = BACKEND_URL + "/search?query=" + query;
        Object movies = restTemplate.getForObject(url, Object.class);
        model.addAttribute("movies", movies);
        return "search";
    }
    @GetMapping("/details/{id}")
    public String movieDetails(@PathVariable int id, Model model) {
    RestTemplate restTemplate = new RestTemplate();
    String url = "http://127.0.0.1:5000/details/" + id;
    Object movieDetails = restTemplate.getForObject(url, Object.class);
    model.addAttribute("movie", movieDetails);
    return "details";
}

}
