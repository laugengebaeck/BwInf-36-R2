package de.lukasrost.bwinf2017.r2_1;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

public class Main {
    private final static int IMPOSSIBLE = -1; //Rückgabekonstanten
    private final static int IMPOSSIBLEPARENT = -2;
    private static int recursionCount = 0; //Rekursionsaufrufe

    public static void main(String[] args) {
        System.out.print("Bitte n der Mauer eingeben: ");
        Scanner scanner = new Scanner(System.in);
        int n = scanner.nextInt();
        if (n < 2){
            System.out.println("n ist zu klein. Keine Lösung möglich!");
            System.exit(0);
        }
        System.out.print("Um wie viele Reihen soll die Höhe reduziert werden? (0=Maximalhöhe):");
        int reihen = scanner.nextInt();
        System.out.println("Starte Backtracking...");
        long beforeTime = System.currentTimeMillis();
        int[][] arr = getSolution(n, reihen);
        long afterTime = System.currentTimeMillis();
        System.out.println("Lösung: ");
        for (int[] anArr : arr){
            System.out.print(" | ");
            for (int anAnArr : anArr) {
                System.out.print(anAnArr + " | ");
            }
        System.out.println();
        }
        System.out.println();
        System.out.println("Benötigte Zeit: " + (afterTime-beforeTime) + " Millisekunden");
        System.out.println("Rekursionsaufrufe: "+ recursionCount);
        compileTikzPicture(arr,n);
    }

    private static int[][] getSolution(int n, int reihen){
        int height = ((n+2)/2) - reihen;
        int[][] solution = new int[height][n]; //Lösungsvektor initialisieren
        for (int z = 1; z <= n; z++){
            solution[0][z-1] = z;
            if (n != 6 && n != 10) {
                solution[1][z - 1] = z + 1;
            }
        }
        solution[1][n-1] = 1;
        boolean[] usedFugen = new boolean[(n*(n+1)/2)+1]; //Fugenliste initialisieren
        Arrays.fill(usedFugen,false);
        int fuge = 0;
        for (int z = 1; z < n; z++){
            fuge += z;
            usedFugen[fuge] = true;
        }
        if (n != 6 && n!= 10) {
            int fuge2 = 0;
            for (int z = 2; z <= n; z++) {
                fuge2 += z;
                usedFugen[fuge2] = true;
            }
        }
        boolean[] usableKloetzeNextEbene = new boolean[n+1]; //nutzbare Kloetze
        Arrays.fill(usableKloetzeNextEbene, true);
        int t = (n == 6 || n== 10) ? 1 : 2; //Startreihe festlegen
        solution = backTrack(n, solution,t,0,usableKloetzeNextEbene,usedFugen, height);
        return solution;
    }

    private static int[][] backTrack(int n, int[][] mauerBefore, int reihe, int klotzInReihe, boolean[] usableKloetze, boolean[] usedFugen, int height){
        recursionCount++;
        if (reihe > (height-1)) return mauerBefore;
        int summe = 0; //vorherige Summe berechnen
        for (int i = 0; i < klotzInReihe; i++){
            summe += mauerBefore[reihe][i];
        }
        boolean[] usableKloetzeNextEbene = Arrays.copyOf(usableKloetze,usableKloetze.length); //Kloetze fuer Rekursion
        for (int klotz=1; klotz<usableKloetze.length; klotz++) {
            if (!usableKloetze[klotz]) continue;
            if (usedFugen[summe + klotz] && ((summe + klotz) != ((n * (n + 1)) / 2))) {
                usableKloetze[klotz] = false; //Klotz an dieser Position nicht nutzbar
            }
        }
        if (reihe != (height-1) && checkPruning(usedFugen, n, usableKloetzeNextEbene, summe)){
            return new int[][]{{IMPOSSIBLEPARENT}}; //erweitertes Pruning checken
        }
        label:
        for (int uk = usableKloetze.length - 1; uk >= 1; uk--) {
            if (!usableKloetze[uk]) continue;
            mauerBefore[reihe][klotzInReihe] = uk; //Datenstrukturen updaten
            usableKloetzeNextEbene[uk] = false;
            usableKloetze[uk] = false;
            if (summe + uk != ((n) * (n + 1)) / 2) {
                usedFugen[summe + uk] = true;
            }
            if (reihe == (height - 1) && klotzInReihe == n - 1) {
                return mauerBefore; //Mauer vollstaendig
            }
            int reiheneu = reihe; //Rekursionsaufruf vorbereiten
            int klotzInReiheNeu = klotzInReihe + 1;
            boolean[] usableKloetzeNextEbene2 = new boolean[n + 1];
            if (klotzInReihe == n - 1) {
                reiheneu = reihe + 1;
                klotzInReiheNeu = 0;
                Arrays.fill(usableKloetzeNextEbene2, true);
            } else {
                usableKloetzeNextEbene2 = Arrays.copyOf(usableKloetzeNextEbene, usableKloetzeNextEbene.length);
            }
            int[][] mauerDanach = backTrack(n, mauerBefore, reiheneu, klotzInReiheNeu, usableKloetzeNextEbene2, usedFugen, height);
            switch (mauerDanach[0][0]) { //Ergebnis auswerten
                case IMPOSSIBLE:
                    usedFugen[summe + uk] = false;
                    usableKloetzeNextEbene[uk] = true;
                    mauerBefore[reihe][klotzInReihe] = 0;
                    break;
                case IMPOSSIBLEPARENT:
                    usedFugen[summe + uk] = false;
                    usableKloetzeNextEbene[uk] = true;
                    mauerBefore[reihe][klotzInReihe] = 0;
                    break label;
                default:
                    return mauerDanach;
            }
        }
        return new int[][]{{IMPOSSIBLE}}; //auf dieser Ebene keine Loesung
    }

    private static boolean checkPruning(boolean[] usedFugen, int n, boolean[] kloetze, int summe){
        int k = n *(n+1) /2;
        ArrayList<Integer> nichtBelegt = new ArrayList<>();
        for (int i = 0; i <= k; i++) {
            if (usedFugen[i]) continue;
            nichtBelegt.add(i); // noch nicht belegte Fugen
        }
        int max = n; //groesster in der Reihe noch nicht verwendeter Klotz
        for (int i = n; i >= 1; i--) {
            if (kloetze[i]) {
                max = i;
                break;
            }
        }
        for (int i=0; i < nichtBelegt.size(); i++) {
            if(i == nichtBelegt.size() -1) continue;
            if (nichtBelegt.get(i+1) - nichtBelegt.get(i) > n){
                return true; //Kriterium Teil 1 erfuellt
            }
        }
        for (int i=0; i < nichtBelegt.size(); i++) {
            if((i == nichtBelegt.size() -1)||(nichtBelegt.get(i) < summe)) continue;
            if (nichtBelegt.get(i+1) - nichtBelegt.get(i) > max){
                return true; //Kriterium Teil 2 erfuellt
            }
        }
        return false;
    }

    private static void compileTikzPicture(int[][] mauer, int n){
        System.out.println("Schreibe und kompiliere jetzt TikZ-Bild der Mauer...");
        StringBuilder latexContent = new StringBuilder();
        latexContent.append("\\documentclass{standalone}\n");
        latexContent.append("\\usepackage{tikz}\n \\begin{document}\n \\begin{tikzpicture} \n");
        latexContent.append("\\draw[very thick] ");
        int x = 0;
        for (int i = 0; i < mauer.length ; i++) {
            x = 0;
            for (int j : mauer[i]) {
                latexContent.append(String.format("(%d, %d) rectangle (%d, %d) ",x,i,x+j,i+1));
                x += j;
            }
        }
        latexContent.append("; \n \\end{tikzpicture}\n \\end{document}");
        String text = latexContent.toString();

        Path path = Paths.get("mauer-"+n+".tex");
        try {
            Files.write(path, text.getBytes());
            Process process = new ProcessBuilder("pdflatex","-synctex=1","-interaction=nonstopmode", path.toAbsolutePath().toString()).redirectOutput(ProcessBuilder.Redirect.DISCARD).start();
            process.waitFor();
        } catch (Exception e) {
            e.printStackTrace();
        }
        System.out.println("Fertig!");
    }
}
