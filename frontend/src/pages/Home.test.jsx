import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { postAPI, storyAPI } from '../api';
import { makePost, page, renderWithAuth } from '../test/render';
import Home from './Home';

vi.mock('../api', async (importOriginal) => ({
  ...(await importOriginal()),
  postAPI: { feed: vi.fn() },
  storyAPI: { list: vi.fn() },
}));

describe('Home feed', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    storyAPI.list.mockResolvedValue(page([]));
  });

  it('loads the next page on demand and appends it', async () => {
    postAPI.feed
      .mockResolvedValueOnce(page([makePost({ id: 1, title: 'First' })], '/api/posts/posts/?page=2'))
      .mockResolvedValueOnce(page([makePost({ id: 2, title: 'Second' })]));
    renderWithAuth(<Home />);

    expect(await screen.findByText('First')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Load more' }));

    expect(await screen.findByText('Second')).toBeInTheDocument();
    expect(screen.getByText('First')).toBeInTheDocument();
    expect(postAPI.feed).toHaveBeenLastCalledWith(2);
    expect(screen.queryByRole('button', { name: 'Load more' })).not.toBeInTheDocument();
  });

  it('shows an empty state', async () => {
    postAPI.feed.mockResolvedValue(page([]));
    renderWithAuth(<Home />);
    expect(await screen.findByText(/Nothing here yet/)).toBeInTheDocument();
  });

  it('shows an error with a retry', async () => {
    postAPI.feed.mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce(page([makePost()]));
    renderWithAuth(<Home />);

    expect(await screen.findByText('The feed could not be loaded.')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Try again' }));
    expect(await screen.findByText('Low tide')).toBeInTheDocument();
  });
});
