package com.secondthorn.solitaireplayer.players.tripeaks;

import com.secondthorn.solitaireplayer.players.MSCWindow;
import com.secondthorn.solitaireplayer.players.PlayException;
import org.sikuli.script.Image;

/**
 * Methods for a TriPeaksPlayer to interact with the Microsoft Solitaire Collection window.
 */
class TriPeaksWindow extends MSCWindow {
    /**
     * The "Undo last move" button that appears when the player runs out of moves.
     */
    private Image undoLastMoveImage;

    TriPeaksWindow() throws InterruptedException, PlayException {
        super("TriPeaks");
        undoLastMoveImage = loadImage("TriPeaks/UndoLastMove.png");
    }

    /**
     * Undo the last move if the "No more moves!" message appears.
     * @return true if the the program undid the last move
     * @throws InterruptedException if the thread is interruped
     * @throws PlayException if unable to click on the button
     */
    boolean undoWhenNoMoreMoves() throws InterruptedException, PlayException {
        return clickImage(undoLastMoveImage, 1.0);
    }

    /**
     * Clicks on one of the 28 tableau cards. The user must make sure it's a valid card to click on: no cards blocking
     * it from below and one rank above or below the card currently on the top of the waste pile.
     *
     * @param index a tableau index from 0 to 27
     * @throws InterruptedException if the thread is interrupted
     */
    void clickTableauCard(int index) throws InterruptedException {
        clickRegion(regions.getTableau()[index]);
    }

    /**
     * Clicks on the stock pile, drawing a card from the stock pile to the waste pile.  The user must make sure the
     * stock pile isn't empty.
     *
     * @throws InterruptedException if the thread is interrupted
     */
    void clickStockCard() throws InterruptedException {
        clickRegion(regions.getStock());
    }

    /**
     * Draws a card from the stock pile to the waste pile. The user must make sure the stock pile is not empty.
     *
     * @throws InterruptedException if the thread is interrupted
     */
    void draw() throws InterruptedException {
        clickRegion(regions.getStock());
    }

    /**
     * Returns the card at the given part of the tableau. The code might guess the wrong card or return "??" for
     * unknown cards.
     *
     * @param index a tableau index from 0 to 27
     * @return the card at that index of the tableau or "??" if unknown
     */
    String cardAtTableau(int index) {
        return cardAt(regions.getTableau()[index]);
    }

    /**
     * Returns the card at the top of the waste pile. The code might guess the wrong card or return "??" for unknown
     * cards.
     *
     * @return the card at the top of the waste pile or "??" if unknown.
     */
    String cardAtWaste() {
        return cardAt(regions.getWaste());
    }
}
