package de.lukasrost.bwinf2017.r2_1;

import java.util.*;

public class Main {
    private final static int IMPOSSIBLE = -1;
    private final static int IMPOSSIBLEPARENT = -2;
    private static int recursionCount = 0;

    public static void main(String[] args) {
        System.out.print("Bitte n der Mauer eingeben: ");
        Scanner scanner = new Scanner(System.in);
        int n = scanner.nextInt();
        if (n < 2){
            System.out.println("n ist zu klein. Keine Lösung möglich!");
            System.exit(0);
        }
        System.out.println("Starte Backtracking...");
        long beforeTime = System.currentTimeMillis();
        int[][] arr = getSolution(n);
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
        System.out.println("Rekursionsaufrufe: "+recursionCount);
    }

    private static int[][] getSolution(int n){
        int[][] solution = new int[(n+2)/2][n];
        for (int z = 1; z <= n; z++){
            solution[0][z-1] = z;
            if (n != 6 && n != 10) {
                solution[1][z - 1] = z + 1;
            }
        }
        solution[1][n-1] = 1;
        boolean[] usedFugen = new boolean[(n*(n+1)/2)+1];
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
        boolean[] usableKloetzeNextEbene = new boolean[n+1];
        Arrays.fill(usableKloetzeNextEbene, true);
        int t = (n == 6 || n== 10) ? 1 : 2;
        solution = backTrack(n, solution,t,0,usableKloetzeNextEbene,usedFugen);
        return solution;
    }

    private static int[][] backTrack(int n, int[][] mauerBefore, int reihe, int klotzInReihe, boolean[] usableKloetze, boolean[] usedFugen){
        recursionCount++;
        if (reihe > ((n+2)/2)-1){
            return mauerBefore;
        }
        int summe = 0;
        for (int i = 0; i < klotzInReihe; i++){
            summe += mauerBefore[reihe][i];
        }
        boolean[] usableKloetzeNextEbene = Arrays.copyOf(usableKloetze,usableKloetze.length);
        for (int klotz=1; klotz<usableKloetze.length; klotz++) {
            if (!usableKloetze[klotz]) continue;
            if (usedFugen[summe + klotz] && ((summe + klotz) != ((n * (n + 1)) / 2))) {
                usableKloetze[klotz] = false;
            }
        }
        if (reihe != (((n+2)/2)-1) && checkPruning(usedFugen, n, usableKloetzeNextEbene, summe)){
            return new int[][]{{IMPOSSIBLEPARENT}};
        }
        label:
        for (int uk = usableKloetze.length - 1; uk >= 1; uk--) {
            if (!usableKloetze[uk]) continue;
            mauerBefore[reihe][klotzInReihe] = uk;
            usableKloetzeNextEbene[uk] = false;
            usableKloetze[uk] = false;
            if (summe + uk != ((n) * (n + 1)) / 2) {
                usedFugen[summe + uk] = true;
            }
            if (reihe == (((n + 2) / 2) - 1) && klotzInReihe == n - 1) {
                return mauerBefore;
            }
            int reiheneu = reihe;
            int klotzInReiheNeu = klotzInReihe + 1;
            boolean[] usableKloetzeNextEbene2 = new boolean[n + 1];
            if (klotzInReihe == n - 1) {
                reiheneu = reihe + 1;
                klotzInReiheNeu = 0;
                Arrays.fill(usableKloetzeNextEbene2, true);
            } else {
                usableKloetzeNextEbene2 = Arrays.copyOf(usableKloetzeNextEbene, usableKloetzeNextEbene.length);
            }
            int[][] mauerDanach = backTrack(n, mauerBefore, reiheneu, klotzInReiheNeu, usableKloetzeNextEbene2, usedFugen);
            switch (mauerDanach[0][0]) {
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
        return new int[][]{{IMPOSSIBLE}};
    }

    private static boolean checkPruning(boolean[] usedFugen, int n, boolean[] kloetze, int summe){
        int k = n *(n+1) /2;
        ArrayList<Integer> nichtBelegt = new ArrayList<>();
        for (int i = 0; i <= k; i++) {
            if (usedFugen[i]) continue;
            nichtBelegt.add(i);
        }
        int min = n;
        for (int i = n; i >= 1; i--) {
            if (kloetze[i]) {
                min = i;
                break;
            }
        }
        boolean ret = false;
        for (int i=0; i < nichtBelegt.size(); i++) {
            if(i == nichtBelegt.size() -1) continue;
            if (nichtBelegt.get(i+1) - nichtBelegt.get(i) > n){
                ret = true;
                break;
            }
        }
        for (int i=0; i < nichtBelegt.size(); i++) {
            if((i == nichtBelegt.size() -1)||(nichtBelegt.get(i) < summe)) continue;
            if (nichtBelegt.get(i+1) - nichtBelegt.get(i) > min){
                ret = true;
                break;
            }
        }
        return ret;
    }
}
